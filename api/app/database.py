import warnings
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, FastAPI, Request, WebSocket
from sqlalchemy import URL, text
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


def create_session_maker(db_url: URL) -> async_sessionmaker:
    engine = create_async_engine(
        url=db_url,
        echo=False,
    )

    return async_sessionmaker(
        bind=engine,
    )


async def get_db_session(
    app: Annotated[FastAPI, Depends(get_app)],
) -> AsyncGenerator[AsyncSession]:
    async with app.state.db_session_maker.begin() as session:
        yield session


async def define_functions_and_triggers(
    db: AsyncSession,
) -> None:
    funcname = await define_function_notify_chat_members_new_message(db)
    await define_trigger_notify_chat_members_new_message(
        db=db,
        funcname=funcname,
    )


async def define_function_notify_chat_members_new_message(
    db: AsyncSession,
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

    await db.execute(stmt)

    return funcname


async def define_trigger_notify_chat_members_new_message(
    db: AsyncSession,
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

    await db.execute(stmt)
