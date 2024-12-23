from datetime import datetime
from typing import TYPE_CHECKING

from asyncpg.types import Range
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import TSTZRANGE, ExcludeConstraint
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.enums import LoanRequestState

from .base import Base, IntegerIdentifier, CreationDate

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

    __table_args__ = (
        ExcludeConstraint(
            (item_id, "="),
            (borrower_id, "="),
            where=(state == LoanRequestState.pending),
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
        server_default=text("tstzrange(now(), 'infinity', '()')"),
    )

    __table_args__ = (
        UniqueConstraint(borrower_id),
        ExcludeConstraint(
            (item_id, "="),
            (during, "&&"),
            name="no_overlapping_date_ranges",
        ),
    )
