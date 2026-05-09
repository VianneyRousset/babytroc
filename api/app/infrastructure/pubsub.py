from broadcaster import Broadcast
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.pubsub import PubsubMessage

_PENDING_NOTIFICATIONS_KEY = "_pending_pubsub_notifications"


def get_broadcast() -> Broadcast:
    return _broadcast


_broadcast: Broadcast
_channel_prefix: str = ""


def init_broadcast_dependency(
    broadcast: Broadcast,
    *,
    channel_prefix: str = "",
) -> None:
    global _broadcast, _channel_prefix
    _broadcast = broadcast
    _channel_prefix = channel_prefix


def user_channel(user_id: int) -> str:
    return f"{_channel_prefix}user{user_id}"


async def notify_user(
    broadcast: Broadcast,
    user_id: int,
    message: PubsubMessage,
) -> None:
    await broadcast.publish(
        channel=user_channel(user_id),
        message=message.model_dump_json(),
    )


def notify_user_after_commit(
    db: AsyncSession,
    broadcast: Broadcast,
    user_id: int,
    message: PubsubMessage,
) -> None:
    """Queue a notification to be published after the session commits.

    Notifications are stored in ``session.info`` and flushed by
    ``flush_pending_notifications`` which must be called after the session
    transaction has been committed (i.e. after the data is visible).
    """
    channel = user_channel(user_id)
    payload = message.model_dump_json()

    pending = db.info.setdefault(_PENDING_NOTIFICATIONS_KEY, [])
    pending.append((broadcast, channel, payload))


async def flush_pending_notifications(db: AsyncSession) -> None:
    """Publish all queued notifications. Call after session commit."""
    pending = db.info.pop(_PENDING_NOTIFICATIONS_KEY, [])
    for broadcast, channel, payload in pending:
        await broadcast.publish(channel=channel, message=payload)
