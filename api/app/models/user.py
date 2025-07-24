import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Identity,
    Integer,
    String,
    func,
    select,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    column_property,
    deferred,
    mapped_column,
    relationship,
    validates,
)
from sqlalchemy.types import UUID, TypeDecorator

from app.utils.hash import HashedStr

from .base import Base, CreationDate
from .item import Item, ItemLike

if TYPE_CHECKING:
    from .loan import Loan, LoanRequest


class HashedString(TypeDecorator):
    """
    String representation of a hashed string.

    Returns a HashedStr when reading.

    Ensure the string is converted to HashedStr
    """

    impl = String
    cache_ok = True

    def process_bind_param(self, value: str | HashedStr | None, dialect) -> str | None:
        if value is None:
            return value
        else:
            return str(HashedStr(value))

    def process_result_value(self, value: str | None, dialect) -> HashedStr | None:
        if value is None:
            return value
        else:
            return HashedStr(value, hash=False)


class User(CreationDate, Base):
    __tablename__ = "user"

    # id is defined explicitly instead of using IntegerIdentifier subclassing
    # to be accessed by likes_count deferred query
    id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=True),
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )
    validated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    validation_code: Mapped[uuid.UUID] = mapped_column(
        UUID,
        index=True,
        unique=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )
    password_hash: Mapped[HashedStr] = mapped_column(
        HashedString,
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

    saved_items: Mapped[list["Item"]] = relationship(
        "Item",
        secondary="item_save",
        back_populates="saved_by",
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
    stars_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    # total number of likes of the items owned by the user
    likes_count: Mapped[int] = deferred(
        column_property(
            select(func.count(ItemLike.item_id))
            .join(Item)
            .where(Item.owner_id == id)
            .scalar_subquery()
        )
    )

    # number of items owned by the user
    items_count: Mapped[int] = deferred(
        column_property(
            select(func.count(Item.id)).where(Item.owner_id == id).scalar_subquery()
        )
    )

    __table_args__ = (CheckConstraint(stars_count >= 0, name="positive_stars_count"),)

    @validates("email")
    def validate_email(self, key, email):
        if "@" not in email:
            msg = f"Invalid email format: {email!r}"
            raise ValueError(msg)
        return email

    def __repr__(self):
        return f"<{self.__class__.__name__} #{self.id!r} {self.email!r} {self.name!r}>"
