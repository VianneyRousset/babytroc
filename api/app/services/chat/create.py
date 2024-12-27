from typing import Optional

from sqlalchemy.orm import Session

from app.clients import database
from app.enums import ChatMessageType
from app.schemas.chat.read import ChatMessageRead


def send_message_text(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
    sender_id: int,
    payload: str,
):
    """Send `text` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.
    """

    return send_message(
        db=db,
        message_type=ChatMessageType.text,
        item_id=item_id,
        borrower_id=borrower_id,
        sender_id=sender_id,
        payload=payload,
    )


def send_message_loan_request_created(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
):
    """Send `loan_request_created` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item borrower.
    """

    return send_message(
        db=db,
        message_type=ChatMessageType.loan_request_created,
        item_id=item_id,
        borrower_id=borrower_id,
        sender_id=borrower_id,
    )


def send_message_loan_request_canceled(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
):
    """Send `loan_request_canceled` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item borrower.
    """

    return send_message(
        db=db,
        message_type=ChatMessageType.loan_request_canceled,
        item_id=item_id,
        borrower_id=borrower_id,
        sender_id=borrower_id,
    )


def send_message_loan_request_accepted(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
):
    """Send `loan_request_accepted` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item owner.
    """

    # get item from database
    item = database.item.get_item(
        db=db,
        item_id=item_id,
    )

    return send_message(
        db=db,
        message_type=ChatMessageType.loan_request_accepted,
        item_id=item_id,
        borrower_id=borrower_id,
        sender_id=item.owner_id,
    )


def send_message_loan_request_rejected(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
):
    """Send `loan_request_rejected` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item owner.
    """

    # get item from database
    item = database.item.get_item(
        db=db,
        item_id=item_id,
    )

    return send_message(
        db=db,
        message_type=ChatMessageType.loan_request_rejected,
        item_id=item_id,
        borrower_id=borrower_id,
        sender_id=item.owner_id,
    )


def send_message_loan_started(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
):
    """Send `loan_started` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item borrower.
    """

    return send_message(
        db=db,
        message_type=ChatMessageType.loan_started,
        item_id=item_id,
        borrower_id=borrower_id,
        sender_id=borrower_id,
    )


def send_message_loan_ended(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
):
    """Send `loan_ended` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item owner.
    """

    # get item from database
    item = database.item.get_item(
        db=db,
        item_id=item_id,
    )

    return send_message(
        db=db,
        message_type=ChatMessageType.loan_ended,
        item_id=item_id,
        borrower_id=borrower_id,
        sender_id=item.owner_id,
    )


def send_message_item_not_available(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
):
    """Send `item_not_available` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item owner.
    """

    # get item from database
    item = database.item.get_item(
        db=db,
        item_id=item_id,
    )

    return send_message(
        db=db,
        message_type=ChatMessageType.item_not_available,
        item_id=item_id,
        borrower_id=borrower_id,
        sender_id=item.owner_id,
    )


def send_message_item_available(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
):
    """Send `item_available` message to chat.

    The chat is identified with `item_id` and `borrower_id`. If the chat does not exist,
    the latter is created.

    The message is sent from the item owner.
    """

    # get item from database
    item = database.item.get_item(
        db=db,
        item_id=item_id,
    )

    return send_message(
        db=db,
        message_type=ChatMessageType.item_available,
        item_id=item_id,
        borrower_id=borrower_id,
        sender_id=item.owner_id,
    )


def send_message(
    db: Session,
    *,
    message_type: ChatMessageType,
    item_id: int,
    borrower_id: int,
    sender_id: int,
    payload: Optional[str] = None,
):
    # ensure chat does exist
    chat = database.chat.ensure_chat(
        db=db,
        item_id=item_id,
        borrower_id=borrower_id,
    )

    message = database.chat.create_message(
        db=db,
        chat=chat,
        message_type=message_type,
        payload=payload,
        sender_id=sender_id,
    )

    return ChatMessageRead.from_orm(message)
