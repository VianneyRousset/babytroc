from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .api.v1 import router as v1_router
from .database import create_session_maker


def create_app(db_url: str) -> FastAPI:
    app = FastAPI()

    app.state.db_session_maker = create_session_maker(db_url)

    @app.get("/")
    async def root(request: Request) -> str:
        return Response()

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": exc.errors()},
        )

    app.include_router(
        router=v1_router,
        prefix="/v1",
    )

    return app
