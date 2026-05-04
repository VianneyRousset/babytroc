import asyncio

from broadcaster import Broadcast
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.pubsub import PubsubMessage


def get_broadcast() -> Broadcast:
    return _broadcast


_broadcast: Broadcast


def init_broadcast_dependency(broadcast: Broadcast) -> None:
    global _broadcast
    _broadcast = broadcast


async def notify_user(
    broadcast: Broadcast,
    user_id: int,
    message: PubsubMessage,
) -> None:
    channel = f"user{user_id}"
    await broadcast.publish(channel=channel, message=message.model_dump_json())


def notify_user_after_commit(
    db: AsyncSession,
    broadcast: Broadcast,
    user_id: int,
    message: PubsubMessage,
) -> None:
    """Schedule a notification to be published after the current transaction commits.

    Uses SQLAlchemy's ``after_commit`` session event so the Redis pub/sub message
    is only sent once the data is visible to other connections.
    """
    channel = f"user{user_id}"
    payload = message.model_dump_json()

    def _on_commit(session):
        asyncio.get_event_loop().call_soon(
            asyncio.ensure_future,
            broadcast.publish(channel=channel, message=payload),
        )

    # Register on the underlying sync session (async session proxies it).
    event.listen(db.sync_session, "after_commit", _on_commit, once=True)
