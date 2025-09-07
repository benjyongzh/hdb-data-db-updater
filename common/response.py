from typing import Any, Optional, Dict

from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse


def success_response(data: Any, status_code: int = 200) -> JSONResponse:
    payload: Dict[str, Any] = {
        "success": True,
        "status": status_code,
        "data": jsonable_encoder(data),
    }
    return JSONResponse(status_code=status_code, content=payload)


def error_response(status_code: int, message: str, code: Optional[int] = None, data: Any = None) -> JSONResponse:
    payload: Dict[str, Any] = {
        "success": False,
        "status": status_code,
        "data": jsonable_encoder(data) if data is not None else None,
        "error": {
            "code": code if code is not None else status_code,
            "message": message,
        },
    }
    return JSONResponse(status_code=status_code, content=payload)

