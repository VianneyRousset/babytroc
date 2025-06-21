from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Integer,
    text,
)
from sqlalchemy.dialects.postgresql import (
    TSTZRANGE,
    ExcludeConstraint,
    Range,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.enums import LoanRequestState
from app.schemas.chat.base import ChatId

from .base import Base, CreationDate, IntegerIdentifier

if TYPE_CHECKING:
    from .item import Item
    from .user import User


class LoanRequest(IntegerIdentifier, CreationDate, Base):
    __tablename__ = "loan_request"

    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "item.id",
            ondelete="CASCADE",  # TODO is this correct ?
        ),
    )
    borrower_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="CASCADE",  # TODO is this correct ?
        ),
    )
    state: Mapped[LoanRequestState] = mapped_column(
        Enum(LoanRequestState),
        default=LoanRequestState.pending,
    )
    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="loan_requests",
        single_parent=True,
    )
    borrower: Mapped["User"] = relationship(
        "User",
        back_populates="borrowing_requests",
        single_parent=True,
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

    @hybrid_property
    def chat_id(self) -> ChatId:
        return ChatId.from_values(
            item_id=self.item_id,
            borrower_id=self.borrower_id,
        )

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
        ForeignKey(
            "item.id",
            ondelete="CASCADE",  # TODO is this correct ?
        ),
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
        single_parent=True,
    )
    borrower: Mapped["User"] = relationship(
        "User",
        back_populates="borrowings",
        single_parent=True,
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
        single_parent=True,
    )

    @hybrid_property
    def owner(self) -> "User":
        return self.item.owner

    @hybrid_property
    def chat_id(self) -> ChatId:
        return ChatId.from_values(
            item_id=self.item_id,
            borrower_id=self.borrower_id,
        )

    @hybrid_property
    def active(self) -> bool:
        return self.during.upper is None

    __table_args__ = (
        ExcludeConstraint(
            (item_id, "="),
            (during, "&&"),
            name="loan_no_overlapping_date_ranges",
            comment="Ensure that two loan of an item does not overlap in time",
        ),
    )
