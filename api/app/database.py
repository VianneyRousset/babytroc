import warnings
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, FastAPI, Request, WebSocket
from sqlalchemy import URL
from sqlalchemy.exc import SAWarning
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# make sqlalchemy warnings as errors
warnings.simplefilter("error", SAWarning)


# trick to get the app from either the request (http/https) or websocket (ws/wss)
def get_app(
    request: Request = None,  # type: ignore[assignment]
    websocket: WebSocket = None,  # type: ignore[assignment]
) -> FastAPI:
    if request is not None:
        return request.app

    if websocket is not None:
        return websocket.app

    msg = "Either request or websocket must be set."
    raise ValueError(msg)


def create_session_maker(db_url: URL, **engine_kwargs) -> async_sessionmaker:
    engine = create_async_engine(
        url=db_url,
        echo=False,
        **engine_kwargs,
    )

    return async_sessionmaker(
        bind=engine,
    )


async def get_db_session(
    app: Annotated[FastAPI, Depends(get_app)],
) -> AsyncGenerator[AsyncSession]:
    async with app.state.db_session_maker.begin() as session:
        yield session
