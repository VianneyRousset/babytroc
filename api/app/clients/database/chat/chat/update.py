from collections.abc import Mapping
from typing import Any

from sqlalchemy.orm import Session

from app.models.chat import Chat


def update_chat(
    db: Session,
    chat: Chat,
    attributes: Mapping[str, Any],
) -> Chat:
    """Update given `attributes` of the `chat`."""

    for key, value in attributes.items():
        setattr(chat, key, value)

    db.flush()
    db.refresh(chat)

    return chat
