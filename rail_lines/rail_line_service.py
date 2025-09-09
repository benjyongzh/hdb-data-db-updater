from typing import Any, Dict, List, Optional
from psycopg2.extras import RealDictCursor

from common.database import db_postgres_conn
from common.util.table_naming import table_name_from_folder
from table_metadata.table_metadata_service import touch_table_metadata
from rail_stations.static_data import LINES


TABLE_NAME = table_name_from_folder(__file__, override_env_var="RAIL_LINES_TABLE")


def list_rail_lines(
    name: Optional[str] = None,
    abbreviation: Optional[str] = None,
    rail_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    where: List[str] = []
    params: List[Any] = []

    if name:
        where.append("LOWER(name) LIKE LOWER(%s)")
        params.append(f"%{name}%")
    if abbreviation:
        where.append("LOWER(abbreviation) = LOWER(%s)")
        params.append(abbreviation)
    if rail_type:
        where.append("LOWER(rail_type) = LOWER(%s)")
        params.append(rail_type)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    sql = f"""
        SELECT id, name, abbreviation, rail_type, colour
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


def get_rail_line_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    sql = f"""
        SELECT id, name, abbreviation, rail_type, colour
        FROM {TABLE_NAME}
        WHERE id = %s
    """
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, [item_id])
            return cur.fetchone()


def refresh_rail_lines_table() -> int:
    """Replace rail_lines table with static LINES mapping from mrt_stations.static_data."""
    rows: List[Dict[str, Any]] = []
    for abbr, meta in LINES.items():
        name = meta.get("name")
        rail_type = meta.get("rail_type")
        colour = meta.get("colour")
        if not name or not rail_type or not colour:
            continue
        rows.append({
            "name": str(name),
            "abbreviation": str(abbr),
            "rail_type": str(rail_type),
            "colour": str(colour),
        })

    with db_postgres_conn() as conn:
        with conn.cursor() as cur:
            # Truncate rail_lines and any dependent rows (e.g., rail_stations_lines)
            cur.execute(f"TRUNCATE TABLE {TABLE_NAME} RESTART IDENTITY CASCADE;")
            if rows:
                cur.executemany(
                    f"""
                    INSERT INTO {TABLE_NAME} (name, abbreviation, rail_type, colour)
                    VALUES (%(name)s, %(abbreviation)s, %(rail_type)s, %(colour)s)
                    """,
                    rows,
                )

    try:
        touch_table_metadata(table_name=TABLE_NAME)
    except Exception:
        pass

    return len(rows)
