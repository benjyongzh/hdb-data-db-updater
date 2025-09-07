from pydantic import BaseModel, Field


class PostalCode(BaseModel):
    id: int = Field(..., ge=0)
    block: str
    street_name: str
    postal_code: str


class PostalCodeFilter(BaseModel):
    block: str | None = None
    street_name: str | None = None
    postal_code: str | None = None
    limit: int = 100
    offset: int = 0

