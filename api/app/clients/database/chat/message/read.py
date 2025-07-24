from sqlalchemy import desc, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.errors.chat import ChatMessageNotFoundError
from app.models.chat import ChatMessage
from app.schemas.chat.query import ChatMessageQueryFilter, ChatMessageQueryPageCursor
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_message(
    db: Session,
    message_id: int,
    *,
    query_filter: ChatMessageQueryFilter | None = None,
) -> ChatMessage:
    """Get message with `message_id`."""

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or ChatMessageQueryFilter()

    stmt = select(ChatMessage).where(ChatMessage.id == message_id)

    stmt = query_filter.apply(stmt)

    try:
        return (db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": message_id}
        raise ChatMessageNotFoundError(key) from error


async def get_message_async(
    db: AsyncSession,
    message_id: int,
    *,
    query_filter: ChatMessageQueryFilter | None = None,
) -> ChatMessage:
    """Get message with `message_id`."""

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or ChatMessageQueryFilter()

    stmt = select(ChatMessage).where(ChatMessage.id == message_id)

    stmt = query_filter.apply(stmt)

    try:
        return (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": message_id}
        raise ChatMessageNotFoundError(key) from error


def list_messages(
    db: Session,
    *,
    query_filter: ChatMessageQueryFilter | None = None,
    page_options: QueryPageOptions | None = None,
) -> QueryPageResult[ChatMessage, ChatMessageQueryPageCursor]:
    """List chat messages matching criteria."""

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or ChatMessageQueryFilter()

    # if no page options are provided, use default page options
    page_options = page_options or QueryPageOptions(
        cursor=ChatMessageQueryPageCursor,
    )

    # selection
    stmt = select(ChatMessage)

    # apply filtering
    stmt = query_filter.apply(stmt)

    # apply ordering
    stmt = stmt.order_by(desc(ChatMessage.id))

    # apply pagination
    stmt = stmt.limit(page_options.limit)
    if page_options.cursor.message_id:
        stmt = stmt.where(ChatMessage.id < page_options.cursor.message_id)

    messages = list(db.execute(stmt).scalars().all())

    return QueryPageResult[ChatMessage, ChatMessageQueryPageCursor](
        data=messages,
        next_page_cursor=ChatMessageQueryPageCursor(
            message_id=messages[-1].id,
        )
        if messages
        else None,
    )
