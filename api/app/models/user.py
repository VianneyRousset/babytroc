from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .base import Base

if TYPE_CHECKING:
    from .item import Item
    from .loan import Loan, LoanRequest


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )
    name: Mapped[str]
    password: Mapped[str]
    creation_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
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
