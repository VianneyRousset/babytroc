from sqlalchemy.orm import Session

from app.clients import database
from app.enums import ReportType
from app.schemas.chat import (
    ChatListRead,
    ChatMessageRead,
    ChatRead,
    ReportCreate,
)


async def get_user_chats_list(db: Session, user_id: int) -> ChatListRead:
    """List all chats where the user with `user_id` participates."""

    # TODO can it be done in one single query ?
    chats = await database.chat.list_chats_with_user(
        db=db,
        user_id=user_id,
    )

    chats = [ChatRead.model_validate(chat) for chat in chats]

    unseen_messages = await database.chat.list_messages(
        db=db,
        receiver_user_id=user_id,
        seen=False,
    )

    unseen_messages = [ChatMessageRead.model_validate(msg) for msg in unseen_messages]

    return ChatListRead(
        chats=chats,
        unseen_messages=unseen_messages,
    )


async def get_user_chat_by_id(
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


async def list_user_chat_messages(
    db: Session,
    user_id: int,
    chat_id: int,
    before_message_id: int,
    count: int,
) -> list[ChatMessageRead]:
    """List messages in chat `chat_id` where the receiver is `user_id`."""

    messages = await database.chat.list_user_chat_messages(
        db=db,
        receiver_user_id=user_id,
        chat_id=chat_id,
        before_message_id=before_message_id,
        count=count,
    )

    return [ChatMessageRead.model_validate(msg) for msg in messages]


async def get_user_chat_message_by_id(
    db: Session,
    chat_id: int,
    user_id: int,
    chat_message_id: int,
) -> ChatMessageRead:
    """Get message with `chat_message_id`.

    The message must have `user_id` as a receiver user ID and `chat_id` as chat ID.
    """

    message = await database.chat.get_user_chat_message_by_id(
        db=db,
        chat_id=chat_id,
        receiver_user_id=user_id,
        chat_message_id=chat_message_id,
    )

    return ChatMessageRead.model_validate(message)


async def mark_user_chat_message_as_seen(
    db: Session,
    user_id: int,
    chat_id: int,
    chat_message_id: int,
) -> ChatMessageRead:
    """Mark message with `chat_message_id` as seen.

    The message must have `user_id` as a receiver user ID and `chat_id` as chat ID.
    """

    message = await database.mark_user_chat_message_as_seen(
        db=db,
        user_id=user_id,
        chat_id=chat_id,
        chat_message_id=chat_message_id,
    )

    return ChatMessageRead.model_validate(message)


async def report_user_chat(
    db: Session,
    user_id: int,
    chat_id: int,
    reported_by_user_id: int,
    report_create: ReportCreate,
):
    """Create a report for the chat with `chat_id`.

    Info about the chat is saved as well as the given client provided description and
    context.

    The chat must have `user_id` as participant.
    """

    chat = await database.chat.get_chat_for_report(
        chat_id=chat_id,
        user_id=user_id,
    )

    await database.report.insert_report(
        report_type=ReportType.chat,
        reported_by_user_id=reported_by_user_id,
        saved_info=chat.json(),
        description=report_create.description,
        context=report_create.context,
    )

    # TODO send an email to moderators
