from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .item import Item


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
        default=func.now(),
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
        "user",
        back_populates="borrowings",
    )

    start_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=None,
        nullable=True,
    )

    # Define the exclusion constraint
    __table_args__ = (
        ExcludeConstraint(
            (func.tstzrange(start_date, end_date, "[)"), "&&"),
            (item_id, "="),
            name="no_overlapping_loans",
        ),
    )
