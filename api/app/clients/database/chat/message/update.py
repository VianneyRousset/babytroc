from collections.abc import Mapping
from typing import Any

from sqlalchemy.orm import Session

from app.models.chat import ChatMessage


def update_message(
    db: Session,
    message: ChatMessage,
    attributes: Mapping[str, Any],
) -> ChatMessage:
    """Update given `attributes` of the chat `message`."""

    for key, value in attributes.items():
        setattr(message, key, value)

    db.flush()
    db.refresh(message)

    return message
