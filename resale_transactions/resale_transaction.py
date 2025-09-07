from typing import Optional
from pydantic import BaseModel, Field


class ResaleTransaction(BaseModel):
    id: int = Field(..., ge=0)
    month: str
    town: str
    flat_type: str
    block: str
    street_name: str
    postal_code_key_id: Optional[int] = None
    storey_range: str
    floor_area_sqm: float
    flat_model: str
    lease_commence_date: int
    remaining_lease: str
    resale_price: float


class ResaleTransactionCreate(BaseModel):
    month: str
    town: str
    flat_type: str
    block: str
    street_name: str
    storey_range: str
    floor_area_sqm: float
    flat_model: str
    lease_commence_date: int
    remaining_lease: str
    resale_price: float


class ResaleTransactionFilter(BaseModel):
    town: Optional[str] = None
    block: Optional[str] = None
    flat_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    limit: int = 100
    offset: int = 0
