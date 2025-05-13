from sqlalchemy.orm import Session

from app.clients import database
from app.pubsub import notify_user
from app.schemas.chat.query import ChatMessageQueryFilter
from app.schemas.chat.read import ChatMessageRead
from app.schemas.pubsub import PubsubMessageUpdatedChatMessage


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

    # get chat
    chat = database.chat.get_chat(
        db=db,
        chat_id=message.chat_id,
    )

    # set seen to True
    message = database.chat.update_message(
        db=db,
        message=message,
        attributes={"seen": True},
    )

    pubsub_message = PubsubMessageUpdatedChatMessage(
        chat_message_id=message.id,
    )

    # notify owner
    notify_user(
        db=db,
        user_id=chat.item.owner_id,
        message=pubsub_message,
    )

    # notify borrower
    notify_user(
        db=db,
        user_id=chat.borrower_id,
        message=pubsub_message,
    )

    return ChatMessageRead.model_validate(message)
