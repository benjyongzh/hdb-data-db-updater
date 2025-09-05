import os
import json
from typing import Any, Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

from common.database import db_postgres_conn


def list_building_polygons(
    block: Optional[str] = None,
    postal_code: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    where = []
    params: List[Any] = []
    if block:
        where.append("LOWER(block) = LOWER(%s)")
        params.append(block)
    if postal_code:
        where.append("postal_code = %s")
        params.append(postal_code)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    sql = f"""
        SELECT id, block, postal_code, postal_code_key_id,
               ST_AsGeoJSON(building_polygon) AS building_polygon
        FROM postalcodes_buildinggeometrypolygon
        {where_sql}
        ORDER BY id
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            # Convert geometry string to JSON
            for r in rows:
                if isinstance(r.get("building_polygon"), str):
                    r["building_polygon"] = json.loads(r["building_polygon"])  # type: ignore
            return rows


def get_building_polygon_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT id, block, postal_code, postal_code_key_id,
               ST_AsGeoJSON(building_polygon) AS building_polygon
        FROM postalcodes_buildinggeometrypolygon
        WHERE id = %s
    """
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, [item_id])
            row = cur.fetchone()
            if row and isinstance(row.get("building_polygon"), str):
                row["building_polygon"] = json.loads(row["building_polygon"])  # type: ignore
            return row

