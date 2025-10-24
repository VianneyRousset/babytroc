from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.errors.chat import ChatNotFoundError
from app.models.chat import Chat
from app.schemas.chat.base import ChatId
from app.schemas.chat.read import ChatRead

from .read import get_chat


def create_chat(
    db: Session,
    chat_id: ChatId,
) -> ChatRead:
    """Create a chat."""

    stmt = (
        insert(Chat)
        .values(
            item_id=chat_id.item_id,
            borrower_id=chat_id.borrower_id,
        )
        .returning(Chat)
    )

    chat = db.execute(stmt).unique().scalars().one()

    return ChatRead.model_validate(
        {
            "id": chat.id,
            "borrower": chat.borrower,
            "owner": chat.owner,
            "item": chat.item,
            "last_message_id": None,
        }
    )


def ensure_chat(
    db: Session,
    chat_id: ChatId,
) -> ChatRead:
    """Create chat if non-existing."""

    try:
        return get_chat(
            db=db,
            chat_id=chat_id,
        )

    except ChatNotFoundError:
        return create_chat(
            db=db,
            chat_id=chat_id,
        )
