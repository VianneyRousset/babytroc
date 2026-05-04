from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.chat import ChatMessageNotFoundError
from app.models.chat import ChatMessage
from app.models.item import Item
from app.pubsub import get_broadcast, notify_user_after_commit
from app.schemas.chat.query import ChatMessageReadQueryFilter
from app.schemas.chat.read import ChatMessageRead
from app.schemas.pubsub import PubsubMessageUpdatedChatMessage


async def mark_message_as_seen(
    db: AsyncSession,
    message_id: int,
    *,
    query_filter: ChatMessageReadQueryFilter | None = None,
) -> ChatMessageRead:
    """Mark message with `message_id` as seen."""

    # default query filter
    query_filter = query_filter or ChatMessageReadQueryFilter()

    # set seen to True
    stmt = (
        update(ChatMessage)
        .where(ChatMessage.id == message_id)
        .values({"seen": True})
        .returning(ChatMessage)
    )

    try:
        message = (await db.execute(stmt)).scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": message_id}
        raise ChatMessageNotFoundError(key) from error

    # notify chat members
    owner_id = (
        await db.execute(
            select(Item.owner_id).where(Item.id == message.item_id)
        )
    ).scalar_one()

    pubsub_message = PubsubMessageUpdatedChatMessage(
        chat_message_id=message.id,
    )
    broadcast = get_broadcast()
    for user_id in {message.borrower_id, owner_id}:
        notify_user_after_commit(db, broadcast, user_id, pubsub_message)

    return ChatMessageRead.model_validate(message)
