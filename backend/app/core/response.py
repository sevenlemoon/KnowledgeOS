from typing import Any

from fastapi.responses import JSONResponse


def success(data: Any = None, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data}


def fail(message: str = "操作失败", code: int = 400) -> JSONResponse:
    return JSONResponse(status_code=200, content={"code": code, "message": message, "data": None})


def paginate(items: list, total: int, page: int, page_size: int) -> dict:
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }
