from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors import ApiError

from .database import create_session_maker
from .routers.v1 import router


def create_app(db_url: str) -> FastAPI:
    app = FastAPI()

    app.state.db_session_maker = create_session_maker(db_url)

    @app.get("/")
    def root(request: Request) -> str:
        return Response()

    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(request: Request, exc: RequestValidationError):
        # TODO extract error message
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ApiError)
    def api_exception_handler(request: Request, error: ApiError):
        return JSONResponse(
            status_code=error.status_code,
            content={
                "status_code": error.status_code,
                "message": error.message,
                "creation_date": error.creation_date.isoformat(),
            },
        )

    app.include_router(
        router=router,
        prefix="/v1",
    )

    return app
