import warnings
from collections.abc import AsyncGenerator, Generator
from typing import Annotated

import sqlalchemy.exc
from fastapi import Depends, FastAPI, Request, WebSocket
from sqlalchemy import URL, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

# make sqlalchemy warnings as errors
warnings.simplefilter("error", sqlalchemy.exc.SAWarning)


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


def create_session_maker(db_url: URL) -> sessionmaker:
    engine = create_engine(db_url, echo=False)

    return sessionmaker(
        bind=engine,
    )


def create_async_session_maker(db_url: URL) -> async_sessionmaker:
    engine = create_async_engine(db_url, echo=False)

    return async_sessionmaker(
        bind=engine,
    )


# TODO switch to connections pool ?
def get_db_session(
    app: Annotated[FastAPI, Depends(get_app)],
) -> Generator[Session]:
    with app.state.db_session_maker.begin() as session:
        yield session


async def get_db_async_session(
    app: Annotated[FastAPI, Depends(get_app)],
) -> AsyncGenerator[AsyncSession]:
    async with app.state.db_async_session_maker.begin() as session:
        yield session
