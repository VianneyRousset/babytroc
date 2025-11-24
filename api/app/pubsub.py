from typing import Annotated

from broadcaster import Broadcast
from fastapi import Depends, FastAPI, Request, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.schemas.pubsub import PubsubMessage


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


def get_broadcast(app: Annotated[FastAPI, Depends(get_app)]) -> Broadcast:
    return app.state.broadcast


def notify_user(
    db: Session,
    user_id: int,
    message: PubsubMessage,
):
    channel = f"user{user_id}"
    db.execute(
        text("SELECT pg_notify(:channel, :payload)"),
        {
            "channel": channel,
            "payload": message.model_dump_json(),
        },
    )


async def notify_user_async(
    db: AsyncSession,
    user_id: int,
    message: PubsubMessage,
):
    channel = f"user{user_id}"
    await db.execute(
        text("SELECT pg_notify(:channel, :payload)"),
        {
            "channel": channel,
            "payload": message.model_dump_json(),
        },
    )
