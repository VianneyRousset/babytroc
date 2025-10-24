from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.clients import database
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

    # get message from database
    message = database.chat.get_message(
        db=db,
        message_id=message_id,
        query_filter=query_filter,
    )

    return ChatMessageRead.model_validate(message)


async def get_message_async(
    db: AsyncSession,
    message_id: int,
    *,
    query_filter: ChatMessageReadQueryFilter | None = None,
) -> ChatMessageRead:
    """Get message with `message_id`."""

    # get message from database
    message = await database.chat.get_message_async(
        db=db,
        message_id=message_id,
        query_filter=query_filter,
    )

    return ChatMessageRead.model_validate(message)


def list_messages(
    db: Session,
    *,
    query_filter: ChatMessageReadQueryFilter | None = None,
    page_options: QueryPageOptions[ChatMessageQueryPageCursor] | None = None,
) -> QueryPageResult[ChatMessageRead, ChatMessageQueryPageCursor]:
    """List messages."""

    # messages in the database
    result = database.chat.list_messages(
        db=db,
        query_filter=query_filter,
        page_options=page_options,
    )

    return QueryPageResult[ChatMessageRead, ChatMessageQueryPageCursor](
        data=[ChatMessageRead.model_validate(message) for message in result.data],
        next_page_cursor=result.next_page_cursor,
    )
