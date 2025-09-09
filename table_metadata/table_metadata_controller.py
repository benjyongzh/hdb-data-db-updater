from typing import List

from fastapi import APIRouter, Body, Query

from table_metadata.table_metadata import (
    TableMetadata,
    TableMetadataTouchRequest,
)
from table_metadata.table_metadata_service import (
    list_table_metadata,
    get_table_metadata_by_id,
    touch_table_metadata,
)
from common.response import success_response, error_response


router = APIRouter(prefix="/table-metadata", tags=["table-metadata"])


@router.get("/")
def list_metadata(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    try:
        rows = list_table_metadata(limit=limit, offset=offset)
        return success_response([TableMetadata(**r) for r in rows])
    except Exception as e:
        return error_response(500, str(e))


@router.get("/{item_id}")
def get_metadata(item_id: int):
    try:
        row = get_table_metadata_by_id(item_id)
        if not row:
            return error_response(404, "Not found")
        return success_response(TableMetadata(**row))
    except Exception as e:
        return error_response(500, str(e))


@router.post("/touch")
def touch_metadata(payload: TableMetadataTouchRequest = Body(...)):
    try:
        payload.require_one()
        row = touch_table_metadata(table_id=payload.table_id, table_name=payload.table_name)
        return success_response(TableMetadata(**row))
    except ValueError as ve:
        return error_response(400, str(ve))
    except Exception as e:
        return error_response(500, str(e))

