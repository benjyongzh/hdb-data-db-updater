from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from rail_stations.rail_station import RailStation
from rail_stations.rail_station_service import (
    list_rail_stations,
    get_rail_station_by_id,
    refresh_rail_stations_table,
)


router = APIRouter(prefix="/api/rail-stations", tags=["rail-stations"])


@router.get("/", response_model=List[RailStation])
def list_stations(
    name: Optional[str] = Query(None),
    ground_level: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    rows = list_rail_stations(
        name=name,
        ground_level=ground_level,
        limit=limit,
        offset=offset,
    )
    return [RailStation(**r) for r in rows]


@router.get("/{item_id}", response_model=RailStation)
def get_station(item_id: int):
    row = get_rail_station_by_id(item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return RailStation(**row)


@router.post("/refresh")
def refresh():
    count = refresh_rail_stations_table()
    return {"inserted": count}

