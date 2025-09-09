import os
import json
from typing import Any, Dict, List, Optional, Tuple
from psycopg2.extras import RealDictCursor

from common.database import db_postgres_conn
from common.util.table_naming import table_name_from_folder
from common.util.download_dataset import (
    get_download_url,
    download_bytes,
    parse_description,
    strip_z_polygon_coords,
)
from table_metadata.table_metadata_service import touch_table_metadata
from rail_stations.static_data import STATIONS

MAIN_TABLE = table_name_from_folder(__file__, override_env_var="RAIL_STATIONS_TABLE")
# Related tables (can be overridden by env if needed)
LINES_TABLE = os.getenv("RAIL_LINES_TABLE", "rail_lines")
LINK_TABLE = os.getenv("RAIL_STATION_LINES_TABLE", f"{MAIN_TABLE}_lines")


def list_rail_stations(
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
        FROM {MAIN_TABLE} AS s
        LEFT JOIN {LINK_TABLE} AS ml ON ml.mrt_station_id = s.id
        LEFT JOIN {LINES_TABLE} AS l ON l.id = ml.line_id
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


def count_rail_stations(
    name: Optional[str] = None,
    ground_level: Optional[str] = None,
) -> int:
    where = []
    params: List[Any] = []
    if name:
        where.append("LOWER(s.name) LIKE LOWER(%s)")
        params.append(f"%{name}%")
    if ground_level:
        where.append("LOWER(s.ground_level) = LOWER(%s)")
        params.append(ground_level)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    sql = f"SELECT COUNT(*) FROM {MAIN_TABLE} AS s {where_sql}"
    with db_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return int(cur.fetchone()[0])


def get_rail_station_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    sql = f"""
        SELECT s.id,
               s.name,
               s.ground_level,
               ST_AsGeoJSON(s.building_polygon) AS building_polygon,
               COALESCE(array_agg(DISTINCT l.abbreviation) FILTER (WHERE l.id IS NOT NULL), ARRAY[]::text[]) AS lines
        FROM {MAIN_TABLE} AS s
        LEFT JOIN {LINK_TABLE} AS ml ON ml.mrt_station_id = s.id
        LEFT JOIN {LINES_TABLE} AS l ON l.id = ml.line_id
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


DATASET_ID = "d_9a6bdc9d93bd041eb0cfbb6a8cb3248f"


def refresh_rail_stations_table() -> int:
    """
    Fetch MRT stations GeoJSON from data.gov.sg, strip Z from coordinates,
    extract NAME and GRND_LEVEL from feature description, and replace the
    entire rail stations table with the new data. Returns inserted row count.
    """

    # 1) Download and parse GeoJSON
    url = get_download_url(DATASET_ID)
    geojson_bytes = download_bytes(url)
    try:
        geojson = json.loads(geojson_bytes.decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"Failed to parse GeoJSON for dataset {DATASET_ID}: {e}")

    if not isinstance(geojson, dict) or geojson.get("type") != "FeatureCollection":
        raise RuntimeError("Expected a GeoJSON FeatureCollection")

    features = geojson.get("features") or []

    # 2) Replace table contents atomically and touch metadata
    with db_postgres_conn() as conn:
        with conn.cursor() as cur:
            # Truncate link table first due to FK to stations, then stations
            cur.execute(f"TRUNCATE TABLE {LINK_TABLE} RESTART IDENTITY;")
            cur.execute(f"TRUNCATE TABLE {MAIN_TABLE} RESTART IDENTITY;")
            # Insert in batches to limit memory usage
            batch: List[Tuple[str, str, str]] = []
            BATCH_SIZE = 500
            inserted = 0
            for feat in features:
                if not isinstance(feat, dict):
                    continue
                props = feat.get("properties") or {}
                geom = feat.get("geometry") or {}

                # Parse attributes from Description HTML
                desc = (props or {}).get("Description") or ""
                meta = parse_description(desc) if isinstance(desc, str) else {}
                name = meta.get("NAME") or meta.get("name")
                ground_level = meta.get("GRND_LEVEL") or meta.get("GRND LEVEL") or meta.get("grnd_level")

                if not name or not ground_level:
                    continue

                if not isinstance(geom, dict) or "type" not in geom or "coordinates" not in geom:
                    continue
                gtype = geom.get("type")
                coords = geom.get("coordinates")
                if gtype == "Polygon" and isinstance(coords, list):
                    coords2d = strip_z_polygon_coords(coords)  # type: ignore[arg-type]
                    cleaned_geom = {"type": "Polygon", "coordinates": coords2d}
                else:
                    continue

                batch.append((str(name), str(ground_level), json.dumps(cleaned_geom)))

                if len(batch) >= BATCH_SIZE:
                    cur.executemany(
                        f"""
                        INSERT INTO {MAIN_TABLE} (name, ground_level, building_polygon)
                        VALUES (
                            %s,
                            %s,
                            ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)
                        )
                        """,
                        batch,
                    )
                    inserted += len(batch)
                    batch.clear()

            if batch:
                cur.executemany(
                    f"""
                    INSERT INTO {MAIN_TABLE} (name, ground_level, building_polygon)
                    VALUES (
                        %s,
                        %s,
                        ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)
                    )
                    """,
                    batch,
                )
                inserted += len(batch)

            # 3) Refresh join table based on static STATIONS mapping
            # Build lookup maps: station name -> id, line abbr -> id
            cur.execute(f"SELECT id, name FROM {MAIN_TABLE};")
            name_to_id = {n.lower(): i for (i, n) in cur.fetchall()}

            cur.execute(f"SELECT id, abbreviation FROM {LINES_TABLE};")
            abbr_to_id = {a.upper(): i for (i, a) in cur.fetchall()}

            # Prepare link rows
            link_rows: List[Tuple[int, int]] = []
            for station_name, line_abbrs in STATIONS.items():
                sid = name_to_id.get(str(station_name).lower())
                if not sid:
                    continue
                for abbr in (line_abbrs or []):
                    lid = abbr_to_id.get(str(abbr).upper())
                    if lid:
                        link_rows.append((sid, lid))

            # Truncate and insert into link table
            cur.execute(f"TRUNCATE TABLE {LINK_TABLE} RESTART IDENTITY;")
            if link_rows:
                cur.executemany(
                    f"""
                    INSERT INTO {LINK_TABLE} (mrt_station_id, line_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    link_rows,
                )

    # Touch table metadata after successful refresh
    try:
        touch_table_metadata(table_name=MAIN_TABLE)
    except Exception:
        pass

    return inserted
