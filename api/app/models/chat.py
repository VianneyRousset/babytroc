from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    Text,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.enums import ChatMessageType
from app.schemas.chat.base import ChatId

from .base import Base, CreationDate, IntegerIdentifier

if TYPE_CHECKING:
    from app.models.item import Item
    from app.models.user import User


class Chat(Base):
    __tablename__ = "chat"

    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "item.id",
            ondelete="CASCADE",
        ),
    )

    borrower_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="CASCADE",
        ),
    )

    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="chats",
        foreign_keys=[item_id],
        single_parent=True,
    )
    borrower: Mapped["User"] = relationship(
        "User",
        foreign_keys=[borrower_id],
        single_parent=True,
    )

    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        cascade="all, delete-orphan",
    )

    @hybrid_property
    def id(self) -> ChatId:
        return ChatId(
            item_id=self.item_id,
            borrower_id=self.borrower_id,
        )

    @hybrid_property
    def owner_id(self) -> int:
        return self.item.owner_id

    @hybrid_property
    def owner(self) -> "User":
        return self.item.owner

    @hybrid_property
    def members_ids(self) -> set[int]:
        return {self.borrower_id, self.item.owner_id}

    @hybrid_property
    def members(self) -> set["User"]:
        return {self.borrower, self.item.owner}

    # check that the sender is a member of the chat
    @validates("messages")
    def validate_message(self, key, msg):
        sender_id = msg.sender.id if msg.sender else msg.sender_id

        if sender_id not in self.members_ids:
            errmsg = f"Sender #{sender_id!r} is not chat members"
            raise ValueError(errmsg)

        return msg

    # TODO cleaner metric ?
    last_message_id: Mapped[int] = mapped_column(default=0)

    __table_args__ = (PrimaryKeyConstraint(item_id, borrower_id),)


class ChatMessage(IntegerIdentifier, CreationDate, Base):
    __tablename__ = "chat_message"

    item_id: Mapped[int] = mapped_column(Integer)

    borrower_id: Mapped[int] = mapped_column(Integer)

    chat: Mapped[Chat] = relationship(
        Chat,
        back_populates="messages",
        foreign_keys=[item_id, borrower_id],
        single_parent=True,
    )

    message_type: Mapped[ChatMessageType] = mapped_column(
        Enum(ChatMessageType),
        default=ChatMessageType.text,
    )

    sender_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="CASCADE",
        ),
    )

    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[sender_id],
        single_parent=True,
    )

    payload: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    seen: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            columns=[item_id, borrower_id],
            refcolumns=[Chat.item_id, Chat.borrower_id],
            ondelete="CASCADE",
        ),
    )
