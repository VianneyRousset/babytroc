from broadcaster import Broadcast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.schemas.pubsub import PubsubMessage


def get_broadcast() -> Broadcast:
    return _broadcast


_broadcast: Broadcast


def init_broadcast_dependency(broadcast: Broadcast) -> None:
    global _broadcast
    _broadcast = broadcast


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
