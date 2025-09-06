from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from psycopg2.extras import RealDictCursor

from common.database import db_postgres_conn
from common.table_naming import table_name_from_folder


METADATA_TABLE = table_name_from_folder(__file__, override_env_var="TABLE_METADATA_TABLE")
REGISTRY_TABLE = os.getenv("DATA_TABLES_TABLE", "data_tables")


def list_table_metadata(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    sql = f"""
        SELECT id, table_id, created_at, updated_at
        FROM {METADATA_TABLE}
        ORDER BY id
        LIMIT %s OFFSET %s
    """
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, [limit, offset])
            return cur.fetchall()


def get_table_metadata_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    sql = f"""
        SELECT id, table_id, created_at, updated_at
        FROM {METADATA_TABLE}
        WHERE id = %s
    """
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, [item_id])
            return cur.fetchone()


def ensure_table_id(table_name: str) -> int:
    sql = f"""
        INSERT INTO {REGISTRY_TABLE} (name)
        VALUES (%s)
        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
        RETURNING id
    """
    with db_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, [table_name])
            return int(cur.fetchone()[0])


def touch_table_metadata_by_table_id(table_id: int) -> Dict[str, Any]:
    sql = f"""
        INSERT INTO {METADATA_TABLE} (table_id)
        VALUES (%s)
        ON CONFLICT (table_id) DO UPDATE SET updated_at = NOW()
        RETURNING id, table_id, created_at, updated_at
    """
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, [table_id])
            return cur.fetchone()


def touch_table_metadata(table_id: Optional[int] = None, table_name: Optional[str] = None) -> Dict[str, Any]:
    if table_id is None:
        if not table_name:
            raise ValueError("Provide either table_id or table_name")
        table_id = ensure_table_id(table_name)
    return touch_table_metadata_by_table_id(table_id)
