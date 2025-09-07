from typing import List, Optional

from fastapi import APIRouter, Query

from postal_codes.postal_code import PostalCode
from postal_codes.postal_code_service import (
    get_postal_code_by_id,
    list_postal_codes as list_postal_codes_svc,
    reset_postal_codes,
)
from tasks.jobs import link_resale_to_postal_codes_task
from common.response import success_response, error_response


router = APIRouter(prefix="/postal-codes", tags=["postal-codes"])


@router.get("/")
def list_postal_codes(
    block: Optional[str] = Query(None),
    street_name: Optional[str] = Query(None),
    postal_code: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    try:
        rows = list_postal_codes_svc(
            block=block,
            street_name=street_name,
            postal_code=postal_code,
            limit=limit,
            offset=offset,
        )
        items = [PostalCode(**r) for r in rows]
        return success_response(items)
    except Exception as e:
        return error_response(500, str(e))


@router.get("/{item_id}")
def get_postal_code(item_id: int):
    try:
        row = get_postal_code_by_id(item_id)
        if not row:
            return error_response(404, "Not found")
        return success_response(PostalCode(**row))
    except Exception as e:
        return error_response(500, str(e))


@router.post("/reset")
def reset(mode: str = Query("clear-links", pattern="^(clear-links|clear-table)$")):
    try:
        result = reset_postal_codes(mode=mode)
        return success_response(result)
    except Exception as e:
        return error_response(500, str(e))


@router.post("/link-resale")
def link_resale_transactions_to_postal_codes():
    try:
        result = link_resale_to_postal_codes_task.delay()
        return success_response({"task_id": result.id})
    except Exception as e:
        return error_response(500, str(e))
