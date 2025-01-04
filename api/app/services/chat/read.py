from typing import Optional

from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.chat.base import ChatId
from app.schemas.chat.query import ChatMessageQueryFilter, ChatQueryFilter
from app.schemas.chat.read import ChatMessageRead, ChatRead
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_chat(
    db: Session,
    *,
    chat_id: ChatId,
    query_filter: Optional[ChatQueryFilter] = None,
) -> ChatRead:
    """Get chat by id."""

    # get chat from database
    chat = database.chat.get_chat(
        db=db,
        chat_id=chat_id,
        query_filter=query_filter,
    )

    return ChatRead.model_validate(chat)


def list_chats(
    db: Session,
    *,
    query_filter: Optional[ChatQueryFilter] = None,
    page_options: Optional[QueryPageOptions] = None,
) -> QueryPageResult[ChatRead]:
    """List chats match criteria."""

    # chats in the database
    result = database.chat.list_chats(
        db=db,
        query_filter=query_filter,
        page_options=page_options,
    )

    return QueryPageResult[ChatRead].cast(result, ChatRead)


def get_message(
    db: Session,
    message_id: int,
    *,
    query_filter: Optional[ChatMessageQueryFilter] = None,
) -> ChatMessageRead:
    """Get message with `message_id`."""

    # get message from database
    message = database.chat.get_message(
        db=db,
        message_id=message_id,
        query_filter=query_filter,
    )

    return ChatMessageRead.model_validate(message)


def list_messages(
    db: Session,
    *,
    query_filter: Optional[ChatMessageQueryFilter] = None,
    page_options: Optional[QueryPageOptions] = None,
) -> QueryPageResult[ChatMessageRead]:
    """List messages."""

    # messages in the database
    result = database.chat.list_messages(
        db=db,
        query_filter=query_filter,
        page_options=page_options,
    )

    return QueryPageResult[ChatMessageRead].cast(result, ChatMessageRead)
