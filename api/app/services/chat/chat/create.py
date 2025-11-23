from sqlalchemy import Integer, column, exists, insert, select, values
from sqlalchemy.orm import Session

from app.models.chat import Chat
from app.schemas.chat.base import ChatId


def ensure_chat(
    db: Session,
    chat_id: ChatId,
) -> None:
    """Create chat with `chat_id`. Skip already if already exists."""

    ensure_many_chats(
        db=db,
        chat_ids={chat_id},
    )


def ensure_many_chats(
    db: Session,
    chat_ids: set[ChatId],
) -> None:
    """Create chats for all `chat_ids`. Skip already existing chats."""

    # values to insert
    chat_values = values(
        column("item_id", Integer),
        column("borrower_id", Integer),
        name="chat_values",
    ).data([(chat_id.item_id, chat_id.borrower_id) for chat_id in chat_ids])

    # insert chats when non-existing
    db.execute(
        insert(Chat).from_select(
            [Chat.item_id, Chat.borrower_id],
            select(chat_values).where(
                ~exists().where(
                    Chat.item_id == chat_values.columns.item_id,
                    Chat.borrower_id == chat_values.columns.borrower_id,
                )
            ),
        )
    )
