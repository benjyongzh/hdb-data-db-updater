from typing import List, Optional

from fastapi import APIRouter, Query

from rail_stations.rail_station import RailStation
from rail_stations.rail_station_service import (
    list_rail_stations,
    get_rail_station_by_id,
)
from tasks.jobs import refresh_rail_stations_task
from common.response import success_response, error_response


router = APIRouter(prefix="/rail-stations", tags=["rail-stations"])


@router.get("/")
def list_stations(
    name: Optional[str] = Query(None),
    ground_level: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    try:
        rows = list_rail_stations(
            name=name,
            ground_level=ground_level,
            limit=limit,
            offset=offset,
        )
        items = [RailStation(**r) for r in rows]
        return success_response(items)
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
