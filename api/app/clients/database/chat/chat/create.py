from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.errors.chat import ChatNotFoundError
from app.models.chat import Chat
from app.models.item import Item
from app.schemas.chat.base import ChatId

from .read import get_chat


def ensure_chat(
    db: Session,
    chat_id: ChatId,
) -> Chat:
    """Get chat with `item_id` and `borrower_id`, create it if needed."""

    try:
        return get_chat(
            db=db,
            chat_id=chat_id,
        )
    except ChatNotFoundError:
        pass

    return create_chat(
        db=db,
        chat_id=chat_id,
    )


def create_chat(
    db: Session,
    chat_id: ChatId,
) -> Chat:
    """Create and insert a chat."""

    stmt = (
        insert(Chat)
        .values(
            item_id=chat_id.item_id,
            borrower_id=chat_id.borrower_id,
        )
        .returning(Chat)
    )

    chat = db.execute(stmt).unique().scalars().one()

    return chat


def insert_chat(
    db: Session,
    *,
    chat: Chat,
    item: Item,
) -> Chat:
    """Insert `chat` into `item`'s chats."""

    item.chats.append(chat)

    db.flush()
    db.refresh(chat)

    return chat
