from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.chat.base import ChatId
from app.schemas.chat.query import ChatQueryFilter, ChatQueryPageCursor
from app.schemas.chat.read import ChatRead
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_chat(
    db: Session,
    *,
    chat_id: ChatId,
    query_filter: ChatQueryFilter | None = None,
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
    query_filter: ChatQueryFilter | None = None,
    page_options: QueryPageOptions | None = None,
) -> QueryPageResult[ChatRead, ChatQueryPageCursor]:
    """List chats match criteria."""

    # chats in the database
    result = database.chat.list_chats(
        db=db,
        query_filter=query_filter,
        page_options=page_options,
    )

    return QueryPageResult[ChatRead, ChatQueryPageCursor](
        data=[ChatRead.model_validate(chat) for chat in result.data],
        next_page_cursor=result.next_page_cursor,
    )
