from sqlalchemy.orm import Session

from app.models.chat import Chat


def delete_chat(
    db: Session,
    chat: Chat,
) -> None:
    """Delete `chat` from database."""

    db.delete(chat)
    db.flush()
