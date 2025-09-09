from typing import List, Optional, Dict

from fastapi import APIRouter, Query, Depends

from rail_stations.rail_station import RailStation
from rail_stations.rail_station_service import (
    list_rail_stations,
    get_rail_station_by_id,
    count_rail_stations,
)
from tasks.jobs import refresh_rail_stations_task
from common.response import success_response, error_response
from common.pagination import pagination_params, build_pagination_meta


router = APIRouter(prefix="/rail-stations", tags=["rail-stations"])


@router.get("/")
def list_stations(
    name: Optional[str] = Query(None),
    ground_level: Optional[str] = Query(None),
    paging: Dict[str, int] = Depends(pagination_params),
):
    try:
        rows = list_rail_stations(
            name=name,
            ground_level=ground_level,
            limit=paging["limit"],
            offset=paging["offset"],
        )
        items = [RailStation(**r) for r in rows]
        total = count_rail_stations(name=name, ground_level=ground_level)
        meta = build_pagination_meta(
            page=paging["page"], page_size=paging["page_size"], total=total, count=len(items)
        )
        return success_response(items, pagination=meta)
    except Exception as e:
        return error_response(500, str(e))


@router.get("/{item_id}")
def get_station(item_id: int):
    try:
        row = get_rail_station_by_id(item_id)
        if not row:
            return error_response(404, "Not found")
        return success_response(RailStation(**row))
    except Exception as e:
        return error_response(500, str(e))


@router.post("/refresh")
def refresh():
    try:
        result = refresh_rail_stations_task.delay()
        return success_response({"task_id": result.id})
    except Exception as e:
        return error_response(500, str(e))
