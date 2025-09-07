from typing import List, Optional

from fastapi import APIRouter, Query

from building_polygons.building_polygon import BuildingPolygon
from building_polygons.building_polygon_service import (
    get_building_polygon_by_id,
    list_building_polygons,
)
from tasks.jobs import refresh_building_polygons_task
from common.response import success_response, error_response


router = APIRouter(prefix="/building-polygons", tags=["building-polygons"])


@router.get("/")
def list_polygons(
    block: Optional[str] = Query(None),
    postal_code: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    try:
        rows = list_building_polygons(
            block=block,
            postal_code=postal_code,
            limit=limit,
            offset=offset,
        )
        items = [BuildingPolygon(**r) for r in rows]
        return success_response(items)
    except Exception as e:
        return error_response(500, str(e))


@router.get("/{item_id}")
def get_polygon(item_id: int):
    try:
        row = get_building_polygon_by_id(item_id)
        if not row:
            return error_response(404, "Not found")
        return success_response(BuildingPolygon(**row))
    except Exception as e:
        return error_response(500, str(e))


@router.post("/refresh")
def refresh_building_polygons():
    try:
        result = refresh_building_polygons_task.delay()
        return success_response({"task_id": result.id})
    except Exception as e:
        return error_response(500, str(e))
