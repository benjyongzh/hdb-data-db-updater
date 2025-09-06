from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from resale_transactions.resale_transaction import ResaleTransaction
from resale_transactions.resale_transaction_service import (
    get_resale_transactions,
    get_resale_transaction_by_id,
    refresh_resale_transaction_table,
)

try:
    # Load .env if present (non-fatal if missing)
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


router = APIRouter(prefix="/api/resale-transactions", tags=["resale-transactions"])


@router.get("/", response_model=List[ResaleTransaction])
def list_resale_transactions(
    town: Optional[str] = Query(None),
    block: Optional[str] = Query(None),
    flat_type: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    return get_resale_transactions(
        town=town,
        block=block,
        flat_type=flat_type,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset,
    )


@router.get("/{item_id}", response_model=ResaleTransaction)
def get_resale_transaction(item_id: int):
    item = get_resale_transaction_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.post("/refresh")
def refresh_resale_transactions():
    """Download latest CSV and refresh the resale_transactions table."""
    try:
        inserted = refresh_resale_transaction_table()
        return {"inserted": inserted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
