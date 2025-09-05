from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from postal_codes.postal_code import PostalCodeAddress
from postal_codes.postal_code_service import (
    get_postal_code_address_by_id,
    list_postal_code_addresses,
)


router = APIRouter(prefix="/api/postal-codes", tags=["postal-codes"])


@router.get("/", response_model=List[PostalCodeAddress])
def list_postal_codes(
    block: Optional[str] = Query(None),
    street_name: Optional[str] = Query(None),
    postal_code: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    rows = list_postal_code_addresses(
        block=block,
        street_name=street_name,
        postal_code=postal_code,
        limit=limit,
        offset=offset,
    )
    return [PostalCodeAddress(**r) for r in rows]


@router.get("/{item_id}", response_model=PostalCodeAddress)
def get_postal_code(item_id: int):
    row = get_postal_code_address_by_id(item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return PostalCodeAddress(**row)

