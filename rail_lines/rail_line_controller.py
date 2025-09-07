from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from rail_lines.rail_line import RailLine
from rail_lines.rail_line_service import (
    list_rail_lines,
    get_rail_line_by_id,
)
from tasks.jobs import refresh_rail_lines_task


router = APIRouter(prefix="/rail-lines", tags=["rail-lines"])


@router.get("/", response_model=List[RailLine])
def list_lines(
    name: Optional[str] = Query(None),
    abbreviation: Optional[str] = Query(None),
    rail_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    rows = list_rail_lines(
        name=name,
        abbreviation=abbreviation,
        rail_type=rail_type,
        limit=limit,
        offset=offset,
    )
    return [RailLine(**r) for r in rows]


@router.get("/{item_id}", response_model=RailLine)
def get_line(item_id: int):
    row = get_rail_line_by_id(item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return RailLine(**row)


@router.post("/refresh")
def refresh():
    result = refresh_rail_lines_task.delay()
    return {"task_id": result.id}
