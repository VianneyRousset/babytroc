from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.clients import database
from app.enums import ChatMessageType
from app.models.chat import ChatMessage
from app.models.item import Item
from app.pubsub import notify_user
from app.schemas.chat.base import ChatId
from app.schemas.chat.read import ChatMessageRead
from app.schemas.pubsub import PubsubMessageNewChatMessage


def send_message_text(
    db: Session,
    *,
    chat_id: ChatId,
    sender_id: int,
    text: str,
) -> ChatMessageRead:
    """Send `text` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.
    """

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.text,
        sender_id=sender_id,
        text=text,
        ensure_chat=False,
    )


def send_message_loan_request_created(
    db: Session,
    chat_id: ChatId,
    loan_request_id: int,
) -> ChatMessageRead:
    """Send `loan_request_created` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item borrower.
    """

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.loan_request_created,
        sender_id=chat_id.borrower_id,
        loan_request_id=loan_request_id,
    )


def send_message_loan_request_cancelled(
    db: Session,
    chat_id: ChatId,
    loan_request_id: int,
) -> ChatMessageRead:
    """Send `loan_request_cancelled` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item borrower.
    """

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.loan_request_cancelled,
        sender_id=chat_id.borrower_id,
        loan_request_id=loan_request_id,
    )


def send_message_loan_request_accepted(
    db: Session,
    chat_id: ChatId,
    loan_request_id: int,
) -> ChatMessageRead:
    """Send `loan_request_accepted` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item owner.
    """

    owner_id = _get_item_owner_id(db, chat_id.item_id)

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.loan_request_accepted,
        sender_id=owner_id,
        loan_request_id=loan_request_id,
    )


def send_message_loan_request_rejected(
    db: Session,
    chat_id: ChatId,
    loan_request_id: int,
) -> ChatMessageRead:
    """Send `loan_request_rejected` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item owner.
    """

    owner_id = _get_item_owner_id(db, chat_id.item_id)

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.loan_request_rejected,
        sender_id=owner_id,
        loan_request_id=loan_request_id,
    )


def send_message_loan_started(
    db: Session,
    chat_id: ChatId,
    loan_id: int,
) -> ChatMessageRead:
    """Send `loan_started` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item borrower.
    """

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.loan_started,
        sender_id=chat_id.borrower_id,
        loan_id=loan_id,
    )


def send_message_loan_ended(
    db: Session,
    chat_id: ChatId,
    loan_id: int,
) -> ChatMessageRead:
    """Send `loan_ended` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item owner.
    """

    owner_id = _get_item_owner_id(db, chat_id.item_id)

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.loan_ended,
        sender_id=owner_id,
        loan_id=loan_id,
    )


def send_message_item_not_available(
    db: Session,
    chat_id: ChatId,
) -> ChatMessageRead:
    """Send `item_not_available` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item owner.
    """

    owner_id = _get_item_owner_id(db, chat_id.item_id)

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.item_not_available,
        sender_id=owner_id,
    )


def send_message_item_available(
    db: Session,
    chat_id: ChatId,
) -> ChatMessageRead:
    """Send `item_available` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item owner.
    """

    owner_id = _get_item_owner_id(db, chat_id.item_id)

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.item_available,
        sender_id=owner_id,
    )


def send_message(
    db: Session,
    *,
    chat_id: ChatId,
    message_type: ChatMessageType,
    sender_id: int,
    text: str | None = None,
    loan_request_id: int | None = None,
    loan_id: int | None = None,
    ensure_chat: bool = True,
) -> ChatMessageRead:
    # ensure chat does exist
    if ensure_chat:
        chat = database.chat.ensure_chat(
            db=db,
            chat_id=chat_id,
        )
    else:
        chat = database.chat.get_chat(
            db=db,
            chat_id=chat_id,
        )

    stmt = (
        insert(ChatMessage)
        .values(
            item_id=chat_id.item_id,
            borrower_id=chat_id.borrower_id,
            message_type=message_type,
            sender_id=sender_id,
            text=text,
            loan_request_id=loan_request_id,
            loan_id=loan_id,
        )
        .returning(ChatMessage)
    )

    # TODO handle constraints violations
    message = db.execute(stmt).unique().scalars().one()

    pubsub_message = PubsubMessageNewChatMessage(
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


def _get_item_owner_id(
    db: Session,
    item_id: int,
) -> int:
    """Get the user_id of the owner of the item with `item_id`."""

    stmt = select(Item.owner_id).where(Item.id == item_id)

    # execute
    # TODO handle not found
    owner_id = db.execute(stmt).unique().scalars().one()

    return owner_id
