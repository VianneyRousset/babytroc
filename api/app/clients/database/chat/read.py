from collections.abc import Collection
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.exception import ChatNotFoundError, ChatMessageNotFoundError
from app.models.chat import Chat, ChatMessage
from app.schemas.chat.query import (
    ChatQueryFilter,
    ChatQueryPageOptions,
    ChatQueryPageResult,
    ChatMessageQueryFilter,
    ChatMessageQueryPageOptions,
    ChatMessageQueryPageResult,
)


def get_chat(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
    query_filter: Optional[ChatQueryFilter] = None,
) -> Chat:
    """Get chat with `item_id` and `borrower_id`."""

    # default query filter
    query_filter = query_filter or ChatQueryFilter()

    stmt = (
        select(Chat)
        .where(Chat.item_id == item_id)
        .where(Chat.borrower_id == borrower_id)
    )

    stmt = query_filter.apply(stmt)

    try:
        return (db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"item_id": item_id, "borrower_id": borrower_id}
        raise ChatNotFoundError(key) from error


def list_chats(
    db: Session,
    *,
    query_filter: Optional[ChatQueryFilter] = None,
    page_options: Optional[ChatQueryPageOptions] = None,
) -> ChatQueryPageResult[Chat]:
    """List chats matching criteria.

    Order
    -----
    The chat are returned sorted by decreasing `last_message_id`.
    """

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or ChatQueryFilter()

    # if no page options are provided, use default page options
    page_options = page_options or ChatQueryPageOptions()

    stmt = select(Chat)

    stmt = query_filter.apply(stmt)
    stmt = page_options.apply(stmt)

    stmt = stmt.order_by(Chat.last_message_id.desc())

    chats = (db.execute(stmt)).scalars().all()

    return ChatQueryPageResult[Chat](
        data=chats,
        query_filter=query_filter,
        page_options=page_options,
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
    page_options: Optional[ChatMessageQueryPageOptions] = None,
) -> ChatMessageQueryPageResult[ChatMessage]:
    """List chat messages matching criteria.

    Order
    -----
    The messages are returned sorted by decreasing `message_id`.
    """

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or ChatMessageQueryFilter()

    # if no page options are provided, use default page options
    page_options = page_options or ChatMessageQueryPageOptions()

    stmt = select(ChatMessage)

    stmt = page_options.apply(stmt)
    stmt = query_filter.apply(stmt)

    stmt = stmt.order_by(ChatMessage.id.desc())

    loans = (db.execute(stmt)).scalars().all()

    return ChatMessageQueryPageResult[ChatMessage](
        data=loans,
        query_filter=query_filter,
        page_options=page_options,
    )
