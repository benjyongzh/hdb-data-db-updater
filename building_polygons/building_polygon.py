from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class BuildingPolygon(BaseModel):
    id: int = Field(..., ge=0)
    block: str
    postal_code: str
    postal_code_key_id: Optional[int] = None
    building_polygon: Dict[str, Any]  # GeoJSON geometry


class BuildingPolygonFilter(BaseModel):
    block: Optional[str] = None
    postal_code: Optional[str] = None
    limit: int = 100
    offset: int = 0

