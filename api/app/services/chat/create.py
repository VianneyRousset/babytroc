
from sqlalchemy.orm import Session

from app.clients import database
from app.enums import ChatMessageType
from app.schemas.chat.base import ChatId
from app.schemas.chat.read import ChatMessageRead


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

    # get item from database
    item = database.item.get_item(
        db=db,
        item_id=chat_id.item_id,
    )

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.loan_request_accepted,
        sender_id=item.owner_id,
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

    # get item from database
    item = database.item.get_item(
        db=db,
        item_id=chat_id.item_id,
    )

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.loan_request_rejected,
        sender_id=item.owner_id,
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

    # get item from database
    item = database.item.get_item(
        db=db,
        item_id=chat_id.item_id,
    )

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.loan_ended,
        sender_id=item.owner_id,
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

    # get item from database
    item = database.item.get_item(
        db=db,
        item_id=chat_id.item_id,
    )

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.item_not_available,
        sender_id=item.owner_id,
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

    # get item from database
    item = database.item.get_item(
        db=db,
        item_id=chat_id.item_id,
    )

    return send_message(
        db=db,
        chat_id=chat_id,
        message_type=ChatMessageType.item_available,
        sender_id=item.owner_id,
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
) -> ChatMessageRead:
    # ensure chat does exist
    chat = database.chat.ensure_chat(
        db=db,
        chat_id=chat_id,
    )

    message = database.chat.create_message(
        db=db,
        chat=chat,
        message_type=message_type,
        sender_id=sender_id,
        text=text,
        loan_request_id=loan_request_id,
        loan_id=loan_id,
    )

    return ChatMessageRead.model_validate(message)
