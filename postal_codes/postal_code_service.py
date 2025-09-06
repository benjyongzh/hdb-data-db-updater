import os
from typing import Any, Dict, List, Optional
from psycopg2.extras import RealDictCursor

from common.database import db_postgres_conn
from common.table_naming import table_name_from_folder

TABLE_NAME = table_name_from_folder(__file__, override_env_var="POSTAL_CODES_TABLE")


def list_postal_code_addresses(
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


def get_postal_code_address_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    sql = f"""
        SELECT id, block, street_name, postal_code
        FROM {TABLE_NAME}
        WHERE id = %s
    """
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, [item_id])
            return cur.fetchone()
