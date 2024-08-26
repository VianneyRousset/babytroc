from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .base import Base

if TYPE_CHECKING:
    from .loan import Loan, LoanRequest
    from .user import User


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str]
    description: Mapped[Optional[str]]
    creation_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
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
        back_populates="item",
        cascade="all, delete",
        passive_deletes=True,
    )
