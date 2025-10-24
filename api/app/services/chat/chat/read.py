from sqlalchemy import desc, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.chat import ChatNotFoundError
from app.models.chat import Chat, ChatMessage
from app.schemas.chat.base import ChatId
from app.schemas.chat.query import ChatQueryPageCursor, ChatReadQueryFilter
from app.schemas.chat.read import ChatRead
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_chat(
    db: Session,
    *,
    chat_id: ChatId,
    query_filter: ChatReadQueryFilter | None = None,
) -> ChatRead:
    """Get chat by id."""

    # default query filter
    query_filter = query_filter or ChatReadQueryFilter()

    stmt = (
        select(Chat, func.max(ChatMessage.id))
        .where(Chat.item_id == chat_id.item_id)
        .where(Chat.borrower_id == chat_id.borrower_id)
        .join(ChatMessage)
        .group_by(Chat.item_id, Chat.borrower_id)
    )

    stmt = query_filter.filter_read(stmt)

    try:
        chat, last_message_id = db.execute(stmt).one()

    except NoResultFound as error:
        key = query_filter.key | {"chat_id": str(chat_id)}
        raise ChatNotFoundError(key) from error

    return ChatRead.model_validate(
        {
            "id": chat.id,
            "borrower": chat.borrower,
            "owner": chat.owner,
            "item": chat.item,
            "last_message_id": last_message_id,
        }
    )


def list_chats(
    db: Session,
    *,
    query_filter: ChatReadQueryFilter | None = None,
    page_options: QueryPageOptions[ChatQueryPageCursor] | None = None,
) -> QueryPageResult[ChatRead, ChatQueryPageCursor]:
    """List chats."""

    # default empty query filter
    query_filter = query_filter or ChatReadQueryFilter()

    # default empty query page options
    page_options = page_options or QueryPageOptions(
        cursor=ChatQueryPageCursor(),
    )

    # selection
    stmt = select(Chat, func.max(ChatMessage.id))

    # apply filtering
    stmt = query_filter.filter_read(stmt)

    # join messages to access chat last message id
    stmt = stmt.join(ChatMessage).group_by(Chat.item_id, Chat.borrower_id)

    # apply ordering
    stmt = stmt.order_by(desc(func.max(ChatMessage.id)))

    # apply pagination
    stmt = stmt.limit(page_options.limit)
    if page_options.cursor.last_message_id:
        stmt = stmt.having(
            func.max(ChatMessage.id) < page_options.cursor.last_message_id
        )

    rows = list(db.execute(stmt).all())

    return QueryPageResult[ChatRead, ChatQueryPageCursor](
        data=[
            ChatRead.model_validate(
                {
                    "id": chat.id,
                    "borrower": chat.borrower,
                    "owner": chat.owner,
                    "item": chat.item,
                    "last_message_id": last_message_id,
                }
            )
            for chat, last_message_id in rows
        ],
        next_page_cursor=ChatQueryPageCursor(
            last_message_id=rows[-1][1],
        )
        if rows
        else None,
    )
