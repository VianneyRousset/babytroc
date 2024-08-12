import os
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

DATABASE_URL = os.environ["DATABASE_URL"]


class NotFoundError(Exception):
    pass


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    name: Mapped[str]
    description: Mapped[Optional[str]]
    creation_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
    )
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
    )
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="items",
    )

    loans: Mapped["Loan"] = relationship(
        "Loan",
        back_populates="item",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    loan_requests: Mapped[list["LoanRequest"]] = relationship(
        "LoanRequest",
        back_populates="items",
        cascade="all, delete",
        passive_deletes=True,
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
    )
    name: Mapped[str]
    password: Mapped[str]
    creation_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
    )

    items: Mapped[list["Item"]] = relationship(
        "Item",
        back_populates="owner",
    )
    borrowings: Mapped[list["Loan"]] = relationship(
        "Loan",
        back_populates="borrower",
    )
    borrowing_requests: Mapped[list["LoanRequest"]] = relationship(
        "LoanRequest",
        back_populates="borrower",
        cascade="all, delete",
        passive_deletes=True,
    )


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
