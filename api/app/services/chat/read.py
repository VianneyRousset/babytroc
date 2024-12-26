from sqlalchemy.orm import Session

from app.clients import database
from app.enums import ReportType
from app.schemas.chat import (
    ChatListRead,
    ChatMessageRead,
    ChatRead,
    ReportCreate,
)


def get_user_chats_list(db: Session, user_id: int) -> ChatListRead:
    """List all chats where the user with `user_id` participates."""

    # TODO can it be done in one single query ?
    chats = database.chat.list_chats_with_user(
        db=db,
        user_id=user_id,
    )

    chats = [ChatRead.model_validate(chat) for chat in chats]

    unseen_messages = database.chat.list_messages(
        db=db,
        receiver_user_id=user_id,
        seen=False,
    )

    unseen_messages = [ChatMessageRead.model_validate(msg) for msg in unseen_messages]

    return ChatListRead(
        chats=chats,
        unseen_messages=unseen_messages,
    )


def get_user_chat_by_id(
    db: Session,
    user_id: int,
    chat_id: int,
) -> ChatRead:
    """Get the chat with ID `chat_id` where the user with `user_id` is a participant."""

    chats = database.chat.list_chats_with_user(
        db=db,
        user_id=user_id,
    )

    # TODO properly handle KeyError -> 404
    chat = next(iter(chat for chat in chats if chat.id == chat_id))

    return ChatRead.model_validate(chat)


def list_user_chat_messages(
    db: Session,
    user_id: int,
    chat_id: int,
    before_message_id: int,
    count: int,
) -> list[ChatMessageRead]:
    """List messages in chat `chat_id` where the receiver is `user_id`."""

    messages = database.chat.list_user_chat_messages(
        db=db,
        receiver_user_id=user_id,
        chat_id=chat_id,
        before_message_id=before_message_id,
        count=count,
    )

    return [ChatMessageRead.model_validate(msg) for msg in messages]


def get_user_chat_message_by_id(
    db: Session,
    chat_id: int,
    user_id: int,
    chat_message_id: int,
) -> ChatMessageRead:
    """Get message with `chat_message_id`.

    The message must have `user_id` as a receiver user ID and `chat_id` as chat ID.
    """

    message = database.chat.get_user_chat_message_by_id(
        db=db,
        chat_id=chat_id,
        receiver_user_id=user_id,
        chat_message_id=chat_message_id,
    )

    return ChatMessageRead.model_validate(message)
