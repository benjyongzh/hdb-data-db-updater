from typing import List, Optional

from fastapi import APIRouter, Query

from rail_lines.rail_line import RailLine
from rail_lines.rail_line_service import (
    list_rail_lines,
    get_rail_line_by_id,
)
from tasks.jobs import refresh_rail_lines_task
from common.response import success_response, error_response


router = APIRouter(prefix="/rail-lines", tags=["rail-lines"])


@router.get("/")
def list_lines(
    name: Optional[str] = Query(None),
    abbreviation: Optional[str] = Query(None),
    rail_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    try:
        rows = list_rail_lines(
            name=name,
            abbreviation=abbreviation,
            rail_type=rail_type,
            limit=limit,
            offset=offset,
        )
        items = [RailLine(**r) for r in rows]
        return success_response(items)
    except Exception as e:
        return error_response(500, str(e))


@router.get("/{item_id}")
def get_line(item_id: int):
    try:
        row = get_rail_line_by_id(item_id)
        if not row:
            return error_response(404, "Not found")
        return success_response(RailLine(**row))
    except Exception as e:
        return error_response(500, str(e))


@router.post("/refresh")
def refresh():
    try:
        result = refresh_rail_lines_task.delay()
        return success_response({"task_id": result.id})
    except Exception as e:
        return error_response(500, str(e))
