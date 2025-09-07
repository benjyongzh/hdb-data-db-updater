from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from postal_codes.postal_code import PostalCode
from postal_codes.postal_code_service import (
    get_postal_code_by_id,
    list_postal_codes as list_postal_codes_svc,
    reset_postal_codes,
)
from tasks.jobs import link_resale_to_postal_codes_task


router = APIRouter(prefix="/api/postal-codes", tags=["postal-codes"])


@router.get("/", response_model=List[PostalCode])
def list_postal_codes(
    block: Optional[str] = Query(None),
    street_name: Optional[str] = Query(None),
    postal_code: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    rows = list_postal_codes_svc(
        block=block,
        street_name=street_name,
        postal_code=postal_code,
        limit=limit,
        offset=offset,
    )
    return [PostalCode(**r) for r in rows]


@router.get("/{item_id}", response_model=PostalCode)
def get_postal_code(item_id: int):
    row = get_postal_code_by_id(item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return PostalCode(**row)


@router.post("/reset")
def reset(mode: str = Query("clear-links", pattern="^(clear-links|clear-table)$")):
    try:
        result = reset_postal_codes(mode=mode)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/link-resale")
def link_resale_transactions_to_postal_codes():
    result = link_resale_to_postal_codes_task.delay()
    return {"task_id": result.id}
