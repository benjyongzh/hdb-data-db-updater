from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, HTTPException, Query

from common.database import db_postgres_conn
from resale_transactions.resale_transaction import (
    ResaleTransaction,
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
    where = []
    params = []
    if town:
        where.append("LOWER(town) = LOWER(%s)")
        params.append(town)
    if block:
        where.append("LOWER(block) = LOWER(%s)")
        params.append(block)
    if flat_type:
        where.append("LOWER(flat_type) = LOWER(%s)")
        params.append(flat_type)
    if min_price is not None:
        where.append("resale_price >= %s")
        params.append(min_price)
    if max_price is not None:
        where.append("resale_price <= %s")
        params.append(max_price)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    sql = f"""
        SELECT id, month, town, flat_type, block, street_name, storey_range,
               floor_area_sqm, flat_model, lease_commence_date, remaining_lease,
               resale_price
        FROM resale_transactions
        {where_sql}
        ORDER BY id
        LIMIT %s OFFSET %s
    """

    params.extend([limit, offset])
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [ResaleTransaction(**r) for r in rows]


@router.get("/{item_id}", response_model=ResaleTransaction)
def get_resale_transaction(item_id: int):
    sql = """
        SELECT id, month, town, flat_type, block, street_name, storey_range,
               floor_area_sqm, flat_model, lease_commence_date, remaining_lease,
               resale_price
        FROM resale_transactions
        WHERE id = %s
    """
    with db_postgres_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, [item_id])
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Not found")
            return ResaleTransaction(**row)
