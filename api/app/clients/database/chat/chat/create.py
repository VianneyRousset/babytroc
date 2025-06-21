from sqlalchemy.orm import Session

from app.clients.database.item import get_item
from app.clients.database.user import get_user
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

    borrower = get_user(
        db=db,
        user_id=chat_id.borrower_id,
    )

    item = get_item(
        db=db,
        item_id=chat_id.item_id,
    )

    chat = Chat(
        borrower=borrower,
    )

    return insert_chat(
        db=db,
        chat=chat,
        item=item,
    )


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
