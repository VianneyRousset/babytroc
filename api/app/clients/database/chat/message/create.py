from sqlalchemy.orm import Session

from app.clients.database.user import get_user
from app.enums import ChatMessageType
from app.models.chat import Chat, ChatMessage


def create_message(
    db: Session,
    *,
    chat: Chat,
    message_type: ChatMessageType,
    sender_id: int,
    text: str | None = None,
    loan_request_id: int | None = None,
    loan_id: int | None = None,
    seen: bool = False,
) -> ChatMessage:
    """Create and insert a chat message into `chat`."""

    sender = get_user(
        db=db,
        user_id=sender_id,
    )

    message = ChatMessage(
        message_type=message_type,
        sender=sender,
        text=text,
        loan_request_id=loan_request_id,
        loan_id=loan_id,
        seen=seen,
    )

    return insert_message(
        db=db,
        chat=chat,
        message=message,
    )


def insert_message(
    db: Session,
    *,
    chat: Chat,
    message: ChatMessage,
) -> ChatMessage:
    """Insert `message` into `chat`."""

    chat.messages.append(message)

    db.flush()
    db.refresh(message)

    # update chat last message id
    chat.last_message_id = message.id

    db.flush()
    db.refresh(chat)

    return message
