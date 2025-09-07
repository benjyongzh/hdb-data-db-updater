from typing import List

from fastapi import APIRouter, HTTPException, Body, Query

from table_metadata.table_metadata import (
    TableMetadata,
    TableMetadataTouchRequest,
)
from table_metadata.table_metadata_service import (
    list_table_metadata,
    get_table_metadata_by_id,
    touch_table_metadata,
)


router = APIRouter(prefix="/table-metadata", tags=["table-metadata"])


@router.get("/", response_model=List[TableMetadata])
def list_metadata(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    rows = list_table_metadata(limit=limit, offset=offset)
    return [TableMetadata(**r) for r in rows]


@router.get("/{item_id}", response_model=TableMetadata)
def get_metadata(item_id: int):
    row = get_table_metadata_by_id(item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return TableMetadata(**row)


@router.post("/touch", response_model=TableMetadata)
def touch_metadata(payload: TableMetadataTouchRequest = Body(...)):
    try:
        payload.require_one()
        row = touch_table_metadata(table_id=payload.table_id, table_name=payload.table_name)
        return TableMetadata(**row)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

