from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RailStation(BaseModel):
    id: int = Field(..., ge=0)
    name: str
    ground_level: str
    building_polygon: Dict[str, Any]
    lines: Optional[List[str]] = None  # abbreviations


class RailStationFilter(BaseModel):
    name: Optional[str] = None
    ground_level: Optional[str] = None
    limit: int = 100
    offset: int = 0

