from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from mrt_stations.mrt_station import MrtStation
from mrt_stations.mrt_station_service import (
    get_mrt_station_by_id,
    list_mrt_stations,
)


router = APIRouter(prefix="/api/mrt-stations", tags=["mrt-stations"])


@router.get("/", response_model=List[MrtStation])
def list_stations(
    name: Optional[str] = Query(None),
    ground_level: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    rows = list_mrt_stations(
        name=name,
        ground_level=ground_level,
        limit=limit,
        offset=offset,
    )
    return [MrtStation(**r) for r in rows]


@router.get("/{item_id}", response_model=MrtStation)
def get_station(item_id: int):
    row = get_mrt_station_by_id(item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return MrtStation(**row)

