from sqlalchemy import desc, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.chat import ChatNotFoundError
from app.models.chat import Chat
from app.schemas.chat.base import ChatId
from app.schemas.chat.query import ChatQueryFilter, ChatQueryPageCursor
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_chat(
    db: Session,
    chat_id: ChatId,
    *,
    query_filter: ChatQueryFilter | None = None,
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
        return db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"chat_id": str(chat_id)}
        raise ChatNotFoundError(key) from error


def list_chats(
    db: Session,
    *,
    query_filter: ChatQueryFilter | None = None,
    page_options: QueryPageOptions | None = None,
) -> QueryPageResult[Chat, ChatQueryPageCursor]:
    """List chats matching criteria."""

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or ChatQueryFilter()

    # if no page options are provided, use default page options
    page_options = page_options or QueryPageOptions(
        cursor=ChatQueryPageCursor(),
    )

    # selection
    stmt = select(Chat)

    # apply filtering
    stmt = query_filter.apply(stmt)

    # apply ordering
    stmt = stmt.order_by(desc(Chat.last_message_id))

    # apply pagination
    stmt = stmt.limit(page_options.limit)
    if page_options.cursor.last_message_id:
        stmt = stmt.where(Chat.last_message_id < page_options.cursor.last_message_id)

    chats = list(db.execute(stmt).scalars().all())

    return QueryPageResult[Chat, ChatQueryPageCursor](
        data=chats,
        next_page_cursor=ChatQueryPageCursor(
            last_message_id=chats[-1].last_message_id,
        ),
    )
