from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from building_polygons.building_polygon import BuildingPolygon
from building_polygons.building_polygon_service import (
    get_building_polygon_by_id,
    list_building_polygons,
)


router = APIRouter(prefix="/api/building-polygons", tags=["building-polygons"])


@router.get("/", response_model=List[BuildingPolygon])
def list_polygons(
    block: Optional[str] = Query(None),
    postal_code: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    rows = list_building_polygons(
        block=block,
        postal_code=postal_code,
        limit=limit,
        offset=offset,
    )
    return [BuildingPolygon(**r) for r in rows]


@router.get("/{item_id}", response_model=BuildingPolygon)
def get_polygon(item_id: int):
    row = get_building_polygon_by_id(item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return BuildingPolygon(**row)

