import os
from typing import Optional, Dict

from fastapi import Query


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default


def default_page_size() -> int:
    """Resolve default page size from env `DEFAULT_PAGE_SIZE` (fallback 100).

    Clamps to a minimum of 1 and a soft maximum of 1000 unless overridden by
    `MAX_PAGE_SIZE`.
    """
    size = _env_int("DEFAULT_PAGE_SIZE", 100)
    max_size = _env_int("MAX_PAGE_SIZE", 1000)
    if size < 1:
        size = 1
    if size > max_size:
        size = max_size
    return size


def resolve_page_size(page_size: Optional[int]) -> int:
    size = page_size if page_size is not None else default_page_size()
    max_size = _env_int("MAX_PAGE_SIZE", 1000)
    if size < 1:
        size = 1
    if size > max_size:
        size = max_size
    return size


def pagination_params(
    page: int = Query(1, ge=1),
    page_size: Optional[int] = Query(None, ge=1),
) -> Dict[str, int]:
    """Compute limit/offset from page and page_size.

    - `page` starts at 1
    - `page_size` defaults to env `DEFAULT_PAGE_SIZE` if omitted
    - result contains: page, page_size, limit, offset
    """
    size = resolve_page_size(page_size)
    offset = (page - 1) * size
    return {"page": page, "page_size": size, "limit": size, "offset": offset}


def build_pagination_meta(page: int, page_size: int, total: int, count: int) -> Dict[str, int]:
    pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
        "count": count,
    }
