from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.chat import ChatMessageNotFoundError
from app.models.chat import ChatMessage
from app.schemas.chat.query import ChatMessageReadQueryFilter
from app.schemas.chat.read import ChatMessageRead


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

    return ChatMessageRead.model_validate(message)
