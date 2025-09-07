from typing import List, Optional
from fastapi import APIRouter, Query

from resale_transactions.resale_transaction import ResaleTransaction
from resale_transactions.resale_transaction_service import (
    get_resale_transactions,
    get_resale_transaction_by_id,
)
from tasks.jobs import refresh_resale_transactions_task
from common.response import success_response, error_response

try:
    # Load .env if present (non-fatal if missing)
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


router = APIRouter(prefix="/resale-transactions", tags=["resale-transactions"])


@router.get("/")
def list_resale_transactions(
    town: Optional[str] = Query(None),
    block: Optional[str] = Query(None),
    flat_type: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    try:
        rows: List[ResaleTransaction] = get_resale_transactions(
            town=town,
            block=block,
            flat_type=flat_type,
            min_price=min_price,
            max_price=max_price,
            limit=limit,
            offset=offset,
        )
        return success_response(rows, status_code=200)
    except Exception as e:
        return error_response(500, str(e))


@router.get("/{item_id}")
def get_resale_transaction(item_id: int):
    try:
        item = get_resale_transaction_by_id(item_id)
        if not item:
            return error_response(404, "Not found")
        return success_response(item, status_code=200)
    except Exception as e:
        return error_response(500, str(e))


@router.post("/refresh")
def refresh_resale_transactions():
    """Enqueue background task to refresh resale transactions and link postal codes."""
    try:
        async_result = refresh_resale_transactions_task.delay()
        return success_response({"task_id": async_result.id}, status_code=200)
    except Exception as e:
        return error_response(500, str(e))
