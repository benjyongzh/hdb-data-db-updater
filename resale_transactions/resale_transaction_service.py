import os
import io
import requests
from datetime import datetime
from django.db import connection, transaction

DATASET_ID = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc"
META_URL = f"https://api-open.data.gov.sg/v1/public/api/datasets/{DATASET_ID}/initiate-download"

# Target table schema (includes id)
TARGET_TABLE = "resale_transactions"
TARGET_COLS = [
    "id",
    "month",
    "town",
    "flat_type",
    "block",
    "street_name",
    "storey_range",
    "floor_area_sqm",
    "flat_model",
    "lease_commence_date",
    "remaining_lease",
    "resale_price",
]

# Staging table matches CSV header exactly (no id column)
STAGING_TABLE = "resale_prices_staging"
STAGING_COLS = TARGET_COLS[1:]  # everything except "id"

def _get_download_url() -> str:
    """
        Fetch dataset from data.gov.sg API using the datastore_search endpoint.
        If a download URL is returned, fetch the actual dataset and save to file.
        """
    r = requests.get(META_URL, timeout=30)
    r.raise_for_status()
    j = r.json()
    url = j.get("data", {}).get("url")
    if not url:
        raise RuntimeError("No download URL in API response")
    return url

def _download_csv_bytes(download_url: str) -> bytes:
    r = requests.get(download_url, timeout=60)
    r.raise_for_status()
    return r.content  # CSV bytes

def refresh_resale_transaction_table() -> int:
    """
    Fetch CSV, load into staging, then replace target table rows.
    Returns number of rows inserted into target.
    """
    download_url = _get_download_url()
    csv_bytes = _download_csv_bytes(download_url)

    # Use DB transaction to make the swap atomic
    with transaction.atomic():
        with connection.cursor() as cur:
            # 1) Create staging (drop if exists)
            cur.execute(f"DROP TABLE IF EXISTS {STAGING_TABLE};")
            # Define explicit types to match your table. Adjust if needed.
            cur.execute(f"""
                CREATE TEMP TABLE {STAGING_TABLE} (
                    month TEXT,
                    town TEXT,
                    flat_type TEXT,
                    block TEXT,
                    street_name TEXT,
                    storey_range TEXT,
                    floor_area_sqm NUMERIC,
                    flat_model TEXT,
                    lease_commence_date INTEGER,
                    remaining_lease TEXT,
                    resale_price NUMERIC
                ) ON COMMIT DROP;
            """)

            # 2) Bulk COPY the raw CSV into staging (HEADER handled by COPY)
            cur.copy_expert(
                f"COPY {STAGING_TABLE} ({', '.join(STAGING_COLS)}) "
                "FROM STDIN WITH (FORMAT csv, HEADER true)",
                file=io.StringIO(csv_bytes.decode("utf-8"))
            )

            # 3) Replace target: truncate, then insert with row_number() as id (starting at 0)
            cur.execute(f"TRUNCATE TABLE {TARGET_TABLE} RESTART IDENTITY;")
            cur.execute(f"""
                INSERT INTO {TARGET_TABLE} ({', '.join(TARGET_COLS)})
                SELECT
                    ROW_NUMBER() OVER (
                        ORDER BY month, town, flat_type, block, street_name, storey_range
                    ) - 1 AS id,
                    month,
                    town,
                    flat_type,
                    block,
                    street_name,
                    storey_range,
                    floor_area_sqm,
                    flat_model,
                    lease_commence_date,
                    remaining_lease,
                    resale_price
                FROM {STAGING_TABLE};
            """)

            # 4) Return count
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_TABLE};")
            count = cur.fetchone()[0]

    return count