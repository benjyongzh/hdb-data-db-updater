from typing import List, Optional, Dict

from fastapi import APIRouter, Query, Depends

from building_polygons.building_polygon import BuildingPolygon
from building_polygons.building_polygon_service import (
    get_building_polygon_by_id,
    list_building_polygons,
    count_building_polygons,
)
from tasks.jobs import refresh_building_polygons_task
from common.response import success_response, error_response
from common.pagination import pagination_params, build_pagination_meta


router = APIRouter(prefix="/building-polygons", tags=["building-polygons"])


@router.get("/")
def list_polygons(
    block: Optional[str] = Query(None),
    postal_code: Optional[str] = Query(None),
    paging: Dict[str, int] = Depends(pagination_params),
):
    try:
        rows = list_building_polygons(
            block=block,
            postal_code=postal_code,
            limit=paging["limit"],
            offset=paging["offset"],
        )
        items = [BuildingPolygon(**r) for r in rows]
        total = count_building_polygons(block=block, postal_code=postal_code)
        meta = build_pagination_meta(
            page=paging["page"], page_size=paging["page_size"], total=total, count=len(items)
        )
        return success_response(items, pagination=meta)
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
