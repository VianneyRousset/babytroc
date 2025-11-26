from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    Text,
    and_,
    or_,
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
            onupdate="CASCADE",
        ),
    )

    borrower_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    item: Mapped["Item"] = relationship(
        "Item",
        foreign_keys=[item_id],
        single_parent=True,
    )
    borrower: Mapped["User"] = relationship(
        "User",
        foreign_keys=[borrower_id],
        single_parent=True,
    )

    @hybrid_property
    def id(self) -> ChatId:
        return ChatId.from_values(
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

    __table_args__ = (PrimaryKeyConstraint(item_id, borrower_id),)


class ChatMessage(IntegerIdentifier, CreationDate, Base):
    __tablename__ = "chat_message"

    item_id: Mapped[int] = mapped_column(Integer)

    borrower_id: Mapped[int] = mapped_column(Integer)

    chat: Mapped[Chat] = relationship(
        Chat,
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
            onupdate="CASCADE",
        ),
    )

    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[sender_id],
        single_parent=True,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    loan_request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "loan_request.id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
    )

    loan_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "loan.id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
    )

    seen: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    @hybrid_property
    def chat_id(self) -> ChatId:
        return ChatId.from_values(
            item_id=self.item_id,
            borrower_id=self.borrower_id,
        )

    __table_args__ = (
        ForeignKeyConstraint(
            columns=[item_id, borrower_id],
            refcolumns=[Chat.item_id, Chat.borrower_id],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        CheckConstraint(
            or_(
                and_(
                    message_type == ChatMessageType.text,
                    text.is_not(None),
                ),
                and_(
                    message_type == ChatMessageType.loan_request_created,
                    loan_request_id.is_not(None),
                ),
                and_(
                    message_type == ChatMessageType.loan_request_cancelled,
                    loan_request_id.is_not(None),
                ),
                and_(
                    message_type == ChatMessageType.loan_request_accepted,
                    loan_request_id.is_not(None),
                ),
                and_(
                    message_type == ChatMessageType.loan_request_rejected,
                    loan_request_id.is_not(None),
                ),
                and_(
                    message_type == ChatMessageType.loan_started,
                    loan_id.is_not(None),
                ),
                and_(
                    message_type == ChatMessageType.loan_ended,
                    loan_id.is_not(None),
                ),
                message_type == ChatMessageType.item_not_available,
                message_type == ChatMessageType.item_available,
            ),
            name="message_type_non_null_attributes",
        ),
    )
