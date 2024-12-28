from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.exception import ChatMessageNotFoundError, ChatNotFoundError
from app.models.chat import Chat, ChatMessage
from app.schemas.chat.base import ChatId
from app.schemas.chat.query import ChatMessageQueryFilter, ChatQueryFilter
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_chat(
    db: Session,
    chat_id: ChatId,
    *,
    query_filter: Optional[ChatQueryFilter] = None,
) -> Chat:
    """Get chat with `chat_id`."""

    # default query filter
    query_filter = query_filter or ChatQueryFilter()

    stmt = (
        select(Chat)
        .where(Chat.item_id == chat_id.item_id)
        .where(Chat.borrower_id == chat_id.borrower_id)
    )

    stmt = query_filter.apply(stmt)

    try:
        return (db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"chat_id": str(chat_id)}
        raise ChatNotFoundError(key) from error


def list_chats(
    db: Session,
    *,
    query_filter: Optional[ChatQueryFilter] = None,
    page_options: Optional[QueryPageOptions] = None,
) -> QueryPageResult[Chat]:
    """List chats matching criteria."""

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or ChatQueryFilter()

    # if no page options are provided, use default page options
    page_options = page_options or QueryPageOptions()

    stmt = select(Chat)

    # apply filtering
    stmt = query_filter.apply(stmt)

    # apply pagination
    stmt = page_options.apply(
        stmt=stmt,
        columns={
            "last_message_date": Chat.last_message_date,
        },
    )

    chats = (db.execute(stmt)).scalars().all()

    return QueryPageResult[Chat](
        data=chats,
        order={
            "last_message_date": [chat.last_message_date for chat in chats],
        },
        desc=page_options.desc,
    )


def get_message(
    db: Session,
    message_id: int,
    *,
    query_filter: Optional[ChatMessageQueryFilter] = None,
) -> ChatMessage:
    """Get message with `message_id`."""

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or ChatMessageQueryFilter()

    stmt = select(ChatMessage).where(ChatMessage.id == message_id)

    stmt = query_filter.apply(stmt)

    try:
        return (db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key() | {"id": message_id}
        raise ChatMessageNotFoundError(key) from error


def list_messages(
    db: Session,
    *,
    query_filter: Optional[ChatMessageQueryFilter] = None,
    page_options: Optional[QueryPageOptions] = None,
) -> QueryPageResult[ChatMessage]:
    """List chat messages matching criteria."""

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or ChatMessageQueryFilter()

    # if no page options are provided, use default page options
    page_options = page_options or QueryPageOptions()

    stmt = select(ChatMessage)

    # apply filtering
    stmt = page_options.apply(stmt)

    # apply pagination
    stmt = query_filter.apply(
        stmt=stmt,
        columns={"message_id": ChatMessage.id},
    )

    messages = (db.execute(stmt)).scalars().all()

    return QueryPageResult[ChatMessage](
        data=messages,
        order={
            "message_id": [message.id for message in messages],
        },
        desc=page_options.desc,
    )
