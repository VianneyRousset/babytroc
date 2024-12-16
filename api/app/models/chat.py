from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
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

from .base import Base, CreationDate, IntegerIdentifier

if TYPE_CHECKING:
    from .user import User


class Chat(IntegerIdentifier, Base):
    __tablename__ = "chat"

    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("item.id"),
    )

    participants: Mapped[list["User"]] = relationship(
        "User",
        secondary="chat_participant",
        back_populates="chats",
    )

    messages: Mapped["ChatMessage"] = relationship(
        "ChatMessage",
        back_populates="chat",
    )


class ChatParticipant(Base):
    __tablename__ = "chat_participant"

    chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chat.id"),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
        primary_key=True,
    )


class ChatMessage(IntegerIdentifier, CreationDate, Base):
    __tablename__ = "chat_message"

    message_type: Mapped[ChatMessageType] = mapped_column(
        Enum(ChatMessageType),
        # server_default=ChatMessageType.text,
    )

    chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chat.id"),
    )

    chat: Mapped["Chat"] = relationship(
        Chat,
        back_populates="messages",
    )

    sender_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
    )

    receiver_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
    )

    payload: Mapped[str] = mapped_column(
        String,
    )

    seen: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
