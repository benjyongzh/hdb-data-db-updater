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

TABLE_NAME = table_name_from_folder(__file__, override_env_var="BUILDING_POLYGONS_TABLE")


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
        FROM {TABLE_NAME}
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
    sql = f"""
        SELECT id, block, postal_code, postal_code_key_id,
               ST_AsGeoJSON(building_polygon) AS building_polygon
        FROM {TABLE_NAME}
        WHERE id = %s
    """
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, [item_id])
            row = cur.fetchone()
            if row and isinstance(row.get("building_polygon"), str):
                row["building_polygon"] = json.loads(row["building_polygon"])  # type: ignore
            return row


DATASET_ID = "d_16b157c52ed637edd6ba1232e026258d"


def refresh_building_polygon_table() -> int:
    """
    Fetch GeoJSON for the configured dataset id, strip Z from all coordinates,
    extract block and postal code from feature descriptions, and replace the
    entire building polygons table with the new data.

    Returns the number of rows inserted.
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

    # 2) Replace table contents atomically; insert rows in batches to limit memory usage
    with db_postgres_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {TABLE_NAME} RESTART IDENTITY;")
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
                block = meta.get("BLK_NO") or meta.get("BLK NO") or meta.get("BLK_NO".lower()) or meta.get("BLK NO".lower())
                postal_code = meta.get("POSTAL_COD") or meta.get("POSTAL COD") or meta.get("POSTAL_COD".lower()) or meta.get("POSTAL COD".lower())

                if not block or not postal_code:
                    # Skip features without required metadata
                    continue

                # Ensure geometry is a Polygon and strip Z
                if not isinstance(geom, dict) or "type" not in geom or "coordinates" not in geom:
                    continue
                gtype = geom.get("type")
                coords = geom.get("coordinates")
                if gtype == "Polygon" and isinstance(coords, list):
                    coords2d = strip_z_polygon_coords(coords)  # type: ignore[arg-type]
                    cleaned_geom = {"type": "Polygon", "coordinates": coords2d}
                else:
                    continue

                batch.append((str(block), str(postal_code), json.dumps(cleaned_geom)))

                if len(batch) >= BATCH_SIZE:
                    cur.executemany(
                        f"""
                        INSERT INTO {TABLE_NAME} (block, postal_code, building_polygon)
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
                    INSERT INTO {TABLE_NAME} (block, postal_code, building_polygon)
                    VALUES (
                        %s,
                        %s,
                        ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)
                    )
                    """,
                    batch,
                )
                inserted += len(batch)
    # Touch table metadata after successful refresh (best-effort)
    try:
        touch_table_metadata(table_name=TABLE_NAME)
    except Exception:
        pass
    return inserted
