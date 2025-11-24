from sqlalchemy import Integer, column, exists, insert, select, values
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat
from app.schemas.chat.base import ChatId


async def ensure_chat(
    db: AsyncSession,
    chat_id: ChatId,
) -> None:
    """Create chat with `chat_id`. Skip already if already exists."""

    await ensure_many_chats(
        db=db,
        chat_ids={chat_id},
    )


async def ensure_many_chats(
    db: AsyncSession,
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

    stmt = insert(Chat).from_select(
        [Chat.item_id, Chat.borrower_id],  # type: ignore[list-item]
        select(chat_values).where(
            ~exists().where(
                Chat.item_id == chat_values.columns.item_id,
                Chat.borrower_id == chat_values.columns.borrower_id,
            )
        ),
    )

    await db.execute(stmt)
