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
from sqlalchemy.dialects.postgresql import TSRANGE, ExcludeConstraint
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.enums import LoanRequestState

from .base import Base

if TYPE_CHECKING:
    from .item import Item
    from .user import User


class LoanRequest(Base):
    __tablename__ = "loan_requests"

    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "items.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    borrower_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    creation_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    state: Mapped[LoanRequestState] = mapped_column(
        Enum(LoanRequestState),
        server_default=LoanRequestState.pending,
    )
    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="loan_requests",
    )
    borrower: Mapped["User"] = relationship(
        "User",
        back_populates="borrowing_requests",
    )


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("items.id"),
    )
    borrower_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "users.id",
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
        TSRANGE,
        server_default=text("tsrange(now(), NULL, '()')"),
    )

    __table_args__ = (
        UniqueConstraint("borrower_id"),
        ExcludeConstraint(
            (item_id, "="),
            ("during", "&&"),
            name="no_overlapping_date_ranges",
        ),
        # optimize the queries using the loaner id
        Index("ix_loan_item_owner", item.owner_id),
    )
