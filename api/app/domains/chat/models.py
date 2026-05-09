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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domains.chat.enums import ChatMessageType
from app.domains.chat.schemas.base import ChatId

from app.shared.models import Base, CreationDate, IntegerIdentifier

if TYPE_CHECKING:
    from app.domains.item.models import Item
    from app.domains.user.models import User


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
        viewonly=True,
        lazy="raise",
    )
    borrower: Mapped["User"] = relationship(
        "User",
        foreign_keys=[borrower_id],
        viewonly=True,
        lazy="raise",
    )

    @hybrid_property
    def id(self) -> ChatId:
        return ChatId.from_values(
            item_id=self.item_id,
            borrower_id=self.borrower_id,
        )

    @property
    def owner_id(self) -> int:
        return self.item.owner_id

    @property
    def owner(self) -> "User":
        return self.item.owner

    @property
    def members_ids(self) -> set[int]:
        return {self.borrower_id, self.item.owner_id}

    @property
    def members(self) -> set["User"]:
        return {self.borrower, self.item.owner}

    __table_args__ = (PrimaryKeyConstraint(item_id, borrower_id),)


class ChatMessage(IntegerIdentifier, CreationDate, Base):
    __tablename__ = "chat_message"

    item_id: Mapped[int] = mapped_column(Integer)

    borrower_id: Mapped[int] = mapped_column(Integer)

    chat: Mapped[Chat] = relationship(
        Chat,
        foreign_keys=[item_id, borrower_id],
        viewonly=True,
        lazy="raise",
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
        index=True,
    )

    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[sender_id],
        viewonly=True,
        lazy="raise",
    )

    text: Mapped[str | None] = mapped_column(
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
