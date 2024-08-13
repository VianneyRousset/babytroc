from datetime import datetime
from typing import Optional

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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .loan import Loan, LoanRequest


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
