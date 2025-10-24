from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.chat import ChatMessageNotFoundError
from app.models.chat import ChatMessage
from app.pubsub import notify_user
from app.schemas.chat.query import ChatMessageReadQueryFilter
from app.schemas.chat.read import ChatMessageRead
from app.schemas.pubsub import PubsubMessageUpdatedChatMessage
from app.services.chat import get_chat


def mark_message_as_seen(
    db: Session,
    message_id: int,
    *,
    query_filter: ChatMessageReadQueryFilter | None = None,
) -> ChatMessageRead:
    """Mark message with `message_id` as seen."""

    # default query filter
    query_filter = query_filter or ChatMessageReadQueryFilter()

    # set seen to True
    stmt = (
        update(ChatMessage)
        .where(ChatMessage.id == message_id)
        .values({"seen": True})
        .returning(ChatMessage)
    )

    try:
        message = db.execute(stmt).scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": message_id}
        raise ChatMessageNotFoundError(key) from error

    # get chat
    chat = get_chat(
        db=db,
        chat_id=message.chat_id,
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
        user_id=chat.id.borrower_id,
        message=pubsub_message,
    )

    return ChatMessageRead.model_validate(message)
