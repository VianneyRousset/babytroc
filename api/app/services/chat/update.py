
from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.chat.query import ChatMessageQueryFilter
from app.schemas.chat.read import ChatMessageRead


def mark_message_as_seen(
    db: Session,
    message_id: int,
    *,
    query_filter: ChatMessageQueryFilter | None = None,
) -> ChatMessageRead:
    """Mark message with `message_id` as seen."""

    # get message from database
    message = database.chat.get_message(
        db=db,
        message_id=message_id,
        query_filter=query_filter,
    )

    # set seen to True
    message = database.chat.update_message(
        db=db,
        message=message,
        attributes={"seen": True},
    )

    return ChatMessageRead.model_validate(message)
