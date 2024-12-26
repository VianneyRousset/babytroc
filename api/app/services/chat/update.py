from sqlalchemy.orm import Session

from app.clients import database
from app.enums import ReportType
from app.schemas.chat import (
    ChatListRead,
    ChatMessageRead,
    ChatRead,
    ReportCreate,
)


def mark_user_chat_message_as_seen(
    db: Session,
    user_id: int,
    chat_id: int,
    chat_message_id: int,
) -> ChatMessageRead:
    """Mark message with `chat_message_id` as seen.

    The message must have `user_id` as a receiver user ID and `chat_id` as chat ID.
    """

    message = database.mark_user_chat_message_as_seen(
        db=db,
        user_id=user_id,
        chat_id=chat_id,
        chat_message_id=chat_message_id,
    )

    return ChatMessageRead.model_validate(message)
