from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import (
    TSTZRANGE,
    ExcludeConstraint,
    Range,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.enums import LoanRequestState

from .base import Base, CreationDate, IntegerIdentifier
from .chat import ChatMessage

if TYPE_CHECKING:
    from .item import Item
    from .user import User


class LoanRequest(IntegerIdentifier, CreationDate, Base):
    __tablename__ = "loan_request"

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
    state: Mapped[LoanRequestState] = mapped_column(
        Enum(LoanRequestState),
        default=LoanRequestState.pending,
    )
    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="loan_requests",
    )
    borrower: Mapped["User"] = relationship(
        "User",
        back_populates="borrowing_requests",
    )

    # once executed, referes to the create loan
    loan_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "loan.id",
        ),
        nullable=True,
        server_default=None,
        comment="The created loan originating from this loan request.",
    )

    loan: Mapped["Loan"] = relationship(
        "Loan",
        back_populates="loan_request",
        single_parent=True,
    )

    creation_message_id: Mapped[int] = mapped_column(ForeignKey(ChatMessage.id))
    creation_chat_message: Mapped[ChatMessage] = relationship(ChatMessage)

    __table_args__ = (
        ExcludeConstraint(
            (item_id, "="),
            (borrower_id, "="),
            where=(state == LoanRequestState.pending),
            name="loan_request_unique_pending_request",
            comment=(
                "Ensure borrower cannot emit two pending loan requests "
                "of the same item."
            ),
        ),
        CheckConstraint(
            (
                ((state == LoanRequestState.executed) & (loan_id.is_not(None)))
                | ((state != LoanRequestState.executed) & (loan_id.is_(None)))
            ),
            name="loan_request_executed_or_not",
            comment="Ensure loan_id is NULL iff state != 'executed'.",
        ),
    )


class Loan(IntegerIdentifier, Base):
    __tablename__ = "loan"

    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("item.id"),
        index=True,
    )
    borrower_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="loans",
    )
    borrower: Mapped["User"] = relationship(
        "User",
        back_populates="borrowings",
    )

    during: Mapped[Range] = mapped_column(
        TSTZRANGE,
        index=True,
        server_default=text("tstzrange(now(), NULL, '()')"),
    )

    # the executed loan request that created this loan
    loan_request: Mapped[LoanRequest] = relationship(
        LoanRequest,
        back_populates="loan",
    )

    # chat messages linked to this loan
    creation_message_id: Mapped[int] = mapped_column(ForeignKey(ChatMessage.id))
    creation_chat_message: Mapped[ChatMessage] = relationship(
        ChatMessage,
        foreign_keys=[creation_message_id],
    )

    __table_args__ = (
        UniqueConstraint(borrower_id),
        ExcludeConstraint(
            (item_id, "="),
            (during, "&&"),
            name="loan_no_overlapping_date_ranges",
            comment="Ensure that two loan of an item does not overlap in time",
        ),
    )
