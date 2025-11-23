import warnings
from collections.abc import AsyncGenerator, Generator
from typing import Annotated

from fastapi import Depends, FastAPI, Request, WebSocket
from sqlalchemy import URL, create_engine, text
from sqlalchemy.exc import SAWarning
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

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


def define_functions_and_triggers(
    db: Session,
) -> None:
    funcname = define_function_notify_chat_members_new_message(db)
    define_trigger_notify_chat_members_new_message(
        db=db,
        funcname=funcname,
    )


def define_function_notify_chat_members_new_message(
    db: Session,
) -> str:
    funcname = "notify_chat_members_new_message"

    stmt = text(
        "\n".join(
            [
                f"CREATE OR REPLACE FUNCTION {funcname}() RETURNS TRIGGER AS $$",
                "DECLARE",
                "    borrower_id INTEGER;",
                "    owner_id INTEGER;",
                "    payload TEXT;",
                "BEGIN",
                "    borrower_id := new.borrower_id;",
                "    SELECT item.owner_id INTO owner_id FROM item",
                "        WHERE item.id = new.item_id;",
                "    payload :=  json_build_object(",
                "        'type', 'new_chat_message',",
                "        'chat_message_id', new.id",
                "    )::text;",
                "    PERFORM pg_notify(format('user%s', borrower_id), payload);",
                "    PERFORM pg_notify(format('user%s', owner_id), payload);",
                "    RETURN NEW;",
                "END;",
                "$$ LANGUAGE plpgsql;",
            ]
        )
    )

    db.execute(stmt)

    return funcname


def define_trigger_notify_chat_members_new_message(
    db: Session,
    *,
    funcname: str,
) -> None:
    stmt = text(
        "\n".join(
            [
                "CREATE OR REPLACE TRIGGER new_chat_message",
                "AFTER INSERT ON chat_message",
                "FOR EACH ROW",
                f"EXECUTE FUNCTION {funcname}();",
            ]
        )
    )

    db.execute(stmt)
