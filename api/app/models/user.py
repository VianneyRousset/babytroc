from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .base import Base, IntegerIdentifier, CreationDate

if TYPE_CHECKING:
    from .chat import Chat
    from .item import Item
    from .loan import Loan, LoanRequest


class User(IntegerIdentifier, CreationDate, Base):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String,
    )
    password: Mapped[str] = mapped_column(
        String,
    )
    avatar_seed: Mapped[str] = mapped_column(
        String,
        server_default=func.md5(text("random()::text")),
    )

    items: Mapped[list["Item"]] = relationship(
        "Item",
        back_populates="owner",
        cascade="all, delete",
    )

    liked_items: Mapped[list["Item"]] = relationship(
        "Item",
        secondary="item_like",
        back_populates="liked_by",
    )

    bookmarked_items: Mapped[list["Item"]] = relationship(
        "Item",
        secondary="item_bookmark",
        back_populates="bookmarked_by",
    )

    borrowings: Mapped[list["Loan"]] = relationship(
        "Loan",
        back_populates="borrower",
    )
    borrowing_requests: Mapped[list["LoanRequest"]] = relationship(
        "LoanRequest",
        back_populates="borrower",
        cascade="all, delete-orphan",
    )
    chats: Mapped[list["Chat"]] = relationship(
        "Chat",
        secondary="chat_participant",
        back_populates="participants",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} #{self.id!r} {self.email!r} {self.name!r}>"
