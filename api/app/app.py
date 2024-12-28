from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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
        return JSONResponse(
            status_code=400,
            content={"detail": exc.errors()},
        )

    app.include_router(
        router=router,
        prefix="/v1",
    )

    return app
