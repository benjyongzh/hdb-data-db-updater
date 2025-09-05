import os
import json
from typing import Any, Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

from common.database import db_postgres_conn


def list_mrt_stations(
    name: Optional[str] = None,
    ground_level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    where = []
    params: List[Any] = []
    if name:
        where.append("LOWER(s.name) LIKE LOWER(%s)")
        params.append(f"%{name}%")
    if ground_level:
        where.append("LOWER(s.ground_level) = LOWER(%s)")
        params.append(ground_level)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    sql = f"""
        SELECT s.id,
               s.name,
               s.ground_level,
               ST_AsGeoJSON(s.building_polygon) AS building_polygon,
               COALESCE(array_agg(DISTINCT l.abbreviation) FILTER (WHERE l.id IS NOT NULL), ARRAY[]::text[]) AS lines
        FROM mrtstations_mrtstation s
        LEFT JOIN mrtstations_mrtstation_lines ml ON ml.mrtstation_id = s.id
        LEFT JOIN mrtstations_line l ON l.id = ml.line_id
        {where_sql}
        GROUP BY s.id
        ORDER BY s.id
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            for r in rows:
                if isinstance(r.get("building_polygon"), str):
                    r["building_polygon"] = json.loads(r["building_polygon"])  # type: ignore
            return rows


def get_mrt_station_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT s.id,
               s.name,
               s.ground_level,
               ST_AsGeoJSON(s.building_polygon) AS building_polygon,
               COALESCE(array_agg(DISTINCT l.abbreviation) FILTER (WHERE l.id IS NOT NULL), ARRAY[]::text[]) AS lines
        FROM mrtstations_mrtstation s
        LEFT JOIN mrtstations_mrtstation_lines ml ON ml.mrtstation_id = s.id
        LEFT JOIN mrtstations_line l ON l.id = ml.line_id
        WHERE s.id = %s
        GROUP BY s.id
    """
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, [item_id])
            row = cur.fetchone()
            if row and isinstance(row.get("building_polygon"), str):
                row["building_polygon"] = json.loads(row["building_polygon"])  # type: ignore
            return row

