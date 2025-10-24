from sqlalchemy import desc, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.errors.chat import ChatMessageNotFoundError
from app.models.chat import ChatMessage
from app.schemas.chat.query import (
    ChatMessageQueryPageCursor,
    ChatMessageReadQueryFilter,
)
from app.schemas.chat.read import ChatMessageRead
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_message(
    db: Session,
    message_id: int,
    *,
    query_filter: ChatMessageReadQueryFilter | None = None,
) -> ChatMessageRead:
    """Get message with `message_id`."""

    # default query filter
    query_filter = query_filter or ChatMessageReadQueryFilter()

    stmt = select(ChatMessage).where(ChatMessage.id == message_id)

    stmt = query_filter.filter_read(stmt)

    try:
        message = db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": message_id}
        raise ChatMessageNotFoundError(key) from error

    return ChatMessageRead.model_validate(message)


async def get_message_async(
    db: AsyncSession,
    message_id: int,
    *,
    query_filter: ChatMessageReadQueryFilter | None = None,
) -> ChatMessageRead:
    """Get message with `message_id`."""

    # default query filter
    query_filter = query_filter or ChatMessageReadQueryFilter()

    stmt = select(ChatMessage).where(ChatMessage.id == message_id)

    stmt = query_filter.filter_read(stmt)

    try:
        message = (await db.execute(stmt)).scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": message_id}
        raise ChatMessageNotFoundError(key) from error

    return ChatMessageRead.model_validate(message)


def list_messages(
    db: Session,
    *,
    query_filter: ChatMessageReadQueryFilter | None = None,
    page_options: QueryPageOptions[ChatMessageQueryPageCursor] | None = None,
) -> QueryPageResult[ChatMessageRead, ChatMessageQueryPageCursor]:
    """List messages."""

    # if no page options are provided, use default page options
    query_filter = query_filter or ChatMessageReadQueryFilter()

    # default query filter
    page_options = page_options or QueryPageOptions(
        cursor=ChatMessageQueryPageCursor(),
    )

    # selection
    stmt = select(ChatMessage)

    # apply filtering
    stmt = query_filter.filter_read(stmt)

    # apply ordering
    stmt = stmt.order_by(desc(ChatMessage.id))

    # apply pagination
    stmt = stmt.limit(page_options.limit)
    if page_options.cursor.message_id:
        stmt = stmt.where(ChatMessage.id < page_options.cursor.message_id)

    messages = list(db.execute(stmt).scalars().all())

    return QueryPageResult[ChatMessageRead, ChatMessageQueryPageCursor](
        data=[ChatMessageRead.model_validate(message) for message in messages],
        next_page_cursor=ChatMessageQueryPageCursor(
            message_id=messages[-1].id,
        )
        if messages
        else None,
    )
