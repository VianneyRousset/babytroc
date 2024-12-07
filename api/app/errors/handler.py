from fastapi import Request
from fastapi.responses import JSONResponse

from .exception import ApiError


def api_error_handler(
    request: Request,
    error: ApiError,
) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={
            "status_code": error.status_code,
            "message": error.message,
            "creation_date": error.creation_date,
        },
    )
