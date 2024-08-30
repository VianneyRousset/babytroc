from fastapi import FastAPI, Request, Response

from .api.v1 import router as v1_router
from .database import create_session_maker


def create_app(db_url: str) -> FastAPI:
    app = FastAPI()

    app.state.db_session_maker = create_session_maker(db_url)

    @app.get("/")
    async def root(request: Request) -> str:
        return Response()

    app.include_router(v1_router)

    return app
