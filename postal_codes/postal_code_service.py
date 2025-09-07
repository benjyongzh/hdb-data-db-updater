from typing import Any, Dict, List, Optional, Tuple
from psycopg2.extras import RealDictCursor
import urllib.parse
import os
import requests
from ratelimit import limits, sleep_and_retry

from common.database import db_postgres_conn
from common.util.table_naming import table_name_from_folder
from postal_codes.postal_code import PostalCode

TABLE_NAME = table_name_from_folder(__file__, override_env_var="POSTAL_CODES_TABLE")
RESALE_TRANSACTIONS_TABLE = os.getenv("RESALE_TRANSACTIONS_TABLE", "resale_transactions")


def list_postal_codes(
    block: Optional[str] = None,
    street_name: Optional[str] = None,
    postal_code: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    where = []
    params: List[Any] = []

    if block:
        where.append("LOWER(block) = LOWER(%s)")
        params.append(block)
    if street_name:
        where.append("LOWER(street_name) = LOWER(%s)")
        params.append(street_name)
    if postal_code:
        where.append("postal_code = %s")
        params.append(postal_code)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    sql = f"""
        SELECT id, block, street_name, postal_code
        FROM {TABLE_NAME}
        {where_sql}
        ORDER BY id
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def get_postal_code_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    sql = f"""
        SELECT id, block, street_name, postal_code
        FROM {TABLE_NAME}
        WHERE id = %s
    """
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, [item_id])
            return cur.fetchone()


# External lookup: OneMap SG (rate-limited)
@sleep_and_retry
@limits(calls=250, period=60)
def get_postal_code_from_address(address: str) -> str:
    encoded_address = urllib.parse.quote(address)
    try:
        response = requests.get(
            f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={encoded_address}&returnGeom=N&getAddrDetails=Y",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json() or {}
        results = data.get("results") or []
        return str(results[0]["POSTAL"]) if results else ""
    except (KeyError, ValueError, IndexError, requests.RequestException) as e:
        try:
            body = response.json()  # type: ignore[name-defined]
        except Exception:
            body = None
        print(f"""
                Error for address {address}:
                {e}
                Response received:
                {body}
            """)
        return ""
    except Exception as e:
        print(f"""
                Unexpected error for address {address}:
                {e}
            """)
        return ""


def create_postalcode_object(block: str, street_name: str) -> PostalCode:
    address_string = f"{block} {street_name}"
    print(f"Attempting to create postal code for: '{address_string}'")
    postal_code: str = get_postal_code_from_address(address_string)
    return PostalCode(block=block, street_name=street_name, postal_code=postal_code)


def ensure_postal_code_row(block: str, street_name: str) -> Optional[Dict[str, Any]]:
    """If a postal_code row for (block, street_name) exists, return it.
    Otherwise, look up the postal code via OneMap and insert a new row.
    Returns the created row dict, or None if lookup failed.
    """
    select_sql = f"""
        SELECT id, block, street_name, postal_code
        FROM {TABLE_NAME}
        WHERE LOWER(block) = LOWER(%s) AND LOWER(street_name) = LOWER(%s)
        LIMIT 1
    """
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(select_sql, [block, street_name])
            existing = cur.fetchone()
            if existing:
                return existing

            # Not found — call external endpoint
            addr = f"{block} {street_name}"
            postal_code = get_postal_code_from_address(addr)
            if not postal_code:
                return None

            insert_sql = f"""
                INSERT INTO {TABLE_NAME} (block, street_name, postal_code)
                VALUES (%s, %s, %s)
                RETURNING id, block, street_name, postal_code
            """
            cur.execute(insert_sql, [block, street_name, postal_code])
            return cur.fetchone()


def backfill_postal_codes_from_resale_transactions(limit: int = 1000, offset: int = 0) -> Dict[str, int]:
    """Extract distinct (block, street_name) from resale transactions that have no postal code row yet,
    fetch postal codes from OneMap, and insert into the postal codes table.

    Returns a summary dict with counts: {"created": n, "failed": n}.
    """
    sql = f"""
        SELECT DISTINCT rt.block, rt.street_name
        FROM {RESALE_TRANSACTIONS_TABLE} AS rt
        LEFT JOIN {TABLE_NAME} AS pc
          ON LOWER(rt.block) = LOWER(pc.block)
         AND LOWER(rt.street_name) = LOWER(pc.street_name)
        WHERE pc.id IS NULL
        ORDER BY rt.block, rt.street_name
        LIMIT %s OFFSET %s
    """
    with db_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, [limit, offset])
            pairs: List[Tuple[str, str]] = cur.fetchall()

    created = 0
    failed = 0
    for block, street_name in pairs:
        row = ensure_postal_code_row(block, street_name)
        if row is None:
            failed += 1
        else:
            created += 1

    return {"created": created, "failed": failed}


def _detect_resale_fk_column() -> Optional[str]:
    """Detect a likely postal code FK column on the resale transactions table."""
    candidates = ["postal_code_key_id", "postal_code_id", "postal_code_key"]
    sql = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
    """
    with db_postgres_conn() as conn:
        with conn.cursor() as cur:
            for name in candidates:
                cur.execute(sql, [RESALE_TRANSACTIONS_TABLE, name])
                if cur.fetchone():
                    return name
    return None


def link_all_resale_transactions_to_postal_codes() -> Dict[str, int]:
    """Link all resale transactions to postal codes via FK.

    1) Bulk-link using existing matches in postal_codes.
    2) For remaining distinct (block, street_name) with no postal code row, create via OneMap and link.
    """
    fk_col = _detect_resale_fk_column()
    if not fk_col:
        raise RuntimeError(
            f"FK column not found on table '{RESALE_TRANSACTIONS_TABLE}'. Expected one of postal_code_key_id/postal_code_id/postal_code_key"
        )

    # Step 1: bulk link existing postal codes
    bulk_sql = f"""
        WITH to_link AS (
            SELECT rt.id, pc.id AS pc_id
            FROM {RESALE_TRANSACTIONS_TABLE} rt
            JOIN {TABLE_NAME} pc
              ON LOWER(rt.block) = LOWER(pc.block)
             AND LOWER(rt.street_name) = LOWER(pc.street_name)
            WHERE rt.{fk_col} IS NULL
        )
        UPDATE {RESALE_TRANSACTIONS_TABLE} AS rt
        SET {fk_col} = t.pc_id
        FROM to_link t
        WHERE rt.id = t.id;
    """
    with db_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(bulk_sql)

    # Step 2: remaining pairs without postal code rows
    remaining_sql = f"""
        SELECT DISTINCT rt.block, rt.street_name
        FROM {RESALE_TRANSACTIONS_TABLE} rt
        LEFT JOIN {TABLE_NAME} pc
          ON LOWER(rt.block) = LOWER(pc.block)
         AND LOWER(rt.street_name) = LOWER(pc.street_name)
        WHERE rt.{fk_col} IS NULL AND pc.id IS NULL
        ORDER BY rt.block, rt.street_name
    """
    with db_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(remaining_sql)
            pairs: List[Tuple[str, str]] = cur.fetchall()

    created = 0
    failed = 0
    for block, street_name in pairs:
        row = ensure_postal_code_row(block, street_name)
        if not row or not row.get("id"):
            failed += 1
            continue
        pc_id = row["id"]
        with db_postgres_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {RESALE_TRANSACTIONS_TABLE}
                    SET {fk_col} = %s
                    WHERE LOWER(block) = LOWER(%s) AND LOWER(street_name) = LOWER(%s) AND {fk_col} IS NULL
                    """,
                    [pc_id, block, street_name],
                )
        created += 1

    return {"created": created, "failed": failed}


def reset_postal_codes(mode: str = "clear-links") -> Dict[str, int]:
    """Reset postal code links or table.

    - clear-links: NULL-out the FK on resale transactions only.
    - clear-table: NULL-out FK and TRUNCATE postal_codes.
    """
    fk_col = _detect_resale_fk_column()
    if not fk_col:
        raise RuntimeError("Postal code FK column not found on resale transactions table")

    summary = {"links_cleared": 0, "table_truncated": 0}
    with db_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE {RESALE_TRANSACTIONS_TABLE} SET {fk_col} = NULL WHERE {fk_col} IS NOT NULL"
            )
            summary["links_cleared"] = 1

    if mode == "clear-table":
        with db_postgres_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"TRUNCATE TABLE {TABLE_NAME} RESTART IDENTITY;")
        summary["table_truncated"] = 1

    return summary
