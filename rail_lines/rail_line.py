from typing import Optional
from pydantic import BaseModel, Field


class RailLine(BaseModel):
    id: int = Field(..., ge=0)
    name: str
    abbreviation: str
    rail_type: str
    colour: str


class RailLineFilter(BaseModel):
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    rail_type: Optional[str] = None
    limit: int = 100
    offset: int = 0
