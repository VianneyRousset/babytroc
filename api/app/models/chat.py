from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.enums import ChatMessageType

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(alway=True),
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("items.id"),
    )

    participants: Mapped[list["User"]] = relationship(
        "User",
        secondary="chat_participants",
        back_populates="chats",
    )

    messages: Mapped["ChatMessage"] = relationship(
        "ChatMessage",
        back_populates="chat",
    )

    __table_args__ = (
        UniqueConstraint(
            "item_id",
            "borrower_id",
            name="unique_item_borrower_chat",
        ),
    )


class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chats.id"),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        primary_key=True,
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    message_type: Mapped[ChatMessageType] = mapped_column(
        Enum(ChatMessageType),
        server_default=ChatMessageType.text,
    )

    chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chats.id"),
    )

    chat: Mapped["Chat"] = relationship(
        Chat,
        back_populates="messages",
    )

    creation_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    seen: Mapped[bool] = mapped_column(
        Boolean,
        server_default=func.false(),
    )

    sender_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
    )

    receiver_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
    )

    payload: Mapped[str] = mapped_column(
        String,
    )
