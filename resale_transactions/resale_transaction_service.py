import io
import os
import tempfile
from typing import List, Optional
from psycopg2.extras import RealDictCursor

from common.database import db_postgres_conn
from common.util.table_naming import table_name_from_folder
from common.util.download_dataset import get_download_url, download_bytes, download_to_file
from resale_transactions.resale_transaction import ResaleTransaction
from table_metadata.table_metadata_service import touch_table_metadata


# Target table schema (includes id)
TARGET_TABLE = table_name_from_folder(__file__, override_env_var="RESALE_TRANSACTIONS_TABLE")
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


def refresh_resale_transaction_table() -> int:
    """
    Fetch CSV, load into staging, then replace target table rows.
    Returns number of rows inserted into target.
    """
    download_url = get_download_url("d_8b84c4ee58e3cfc0ece0d773c8ca6abc")
    # Stream to a temporary file to avoid large in-memory buffers
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix="resale_prices_", suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name
            download_to_file(download_url, tmp)

        # Use a single psycopg2 connection to ensure atomic swap
        with db_postgres_conn() as conn:
            with conn.cursor() as cur:
                # 1) Create staging (drop if exists). Use a temporary table scoped to this connection
                cur.execute(f"DROP TABLE IF EXISTS {STAGING_TABLE};")
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
                with open(tmp_path, "r", encoding="utf-8", newline="") as f:
                    cur.copy_expert(
                        f"COPY {STAGING_TABLE} ({', '.join(STAGING_COLS)}) "
                        "FROM STDIN WITH (FORMAT csv, HEADER true)",
                        file=f,
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

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    # Touch table metadata after a successful refresh
    try:
        touch_table_metadata(table_name=TARGET_TABLE)
    except Exception:
        # Best-effort; do not fail the refresh if metadata touch fails
        pass

    return count


# Read services
def get_resale_transactions(
    town: Optional[str] = None,
    block: Optional[str] = None,
    flat_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[ResaleTransaction]:
    where = []
    params = []
    if town:
        where.append("LOWER(town) = LOWER(%s)")
        params.append(town)
    if block:
        where.append("LOWER(block) = LOWER(%s)")
        params.append(block)
    if flat_type:
        where.append("LOWER(flat_type) = LOWER(%s)")
        params.append(flat_type)
    if min_price is not None:
        where.append("resale_price >= %s")
        params.append(min_price)
    if max_price is not None:
        where.append("resale_price <= %s")
        params.append(max_price)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    sql = f"""
        SELECT id, month, town, flat_type, block, street_name, postal_code_key_id, storey_range,
               floor_area_sqm, flat_model, lease_commence_date, remaining_lease,
               resale_price
        FROM {TARGET_TABLE}
        {where_sql}
        ORDER BY id
        LIMIT %s OFFSET %s
    """

    params.extend([limit, offset])
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [ResaleTransaction(**r) for r in rows]


def count_resale_transactions(
    town: Optional[str] = None,
    block: Optional[str] = None,
    flat_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> int:
    where = []
    params = []
    if town:
        where.append("LOWER(town) = LOWER(%s)")
        params.append(town)
    if block:
        where.append("LOWER(block) = LOWER(%s)")
        params.append(block)
    if flat_type:
        where.append("LOWER(flat_type) = LOWER(%s)")
        params.append(flat_type)
    if min_price is not None:
        where.append("resale_price >= %s")
        params.append(min_price)
    if max_price is not None:
        where.append("resale_price <= %s")
        params.append(max_price)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    sql = f"SELECT COUNT(*) FROM {TARGET_TABLE} {where_sql}"
    with db_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return int(cur.fetchone()[0])


def get_resale_transaction_by_id(item_id: int) -> Optional[ResaleTransaction]:
    sql = f"""
        SELECT id, month, town, flat_type, block, street_name, postal_code_key_id, storey_range,
               floor_area_sqm, flat_model, lease_commence_date, remaining_lease,
               resale_price
        FROM {TARGET_TABLE}
        WHERE id = %s
    """
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, [item_id])
            row = cur.fetchone()
            return ResaleTransaction(**row) if row else None
