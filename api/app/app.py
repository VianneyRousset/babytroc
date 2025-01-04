from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors import ApiError

from .config import Config
from .database import create_session_maker
from .routers.v1 import router


def create_app(config: Config) -> FastAPI:
    app = FastAPI()

    app.state.config = config
    app.state.db_session_maker = create_session_maker(config.postgres_url)

    @app.get("/")
    def root(request: Request) -> JSONResponse:
        return JSONResponse(
            status_code=200,
            content={"status": "ok"},
        )

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
