from datetime import datetime
from typing import TYPE_CHECKING, Optional

from asyncpg.types import Range
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Boolean,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import INT4RANGE
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
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str]
    description: Mapped[Optional[str]]
    images: Mapped[list["ItemImage"]] = relationship(
        "ItemImage",
        back_populates="item",
        cascade="all, delete",
        passive_deletes=True,
    )
    regions: Mapped[list["Region"]] = relationship(
        "Region",
        secondary="ItemToRegion",
        back_populates="items",
    )
    targeted_age: Mapped[Range] = mapped_column(
        INT4RANGE,
        server_default=text("int4range(0, NULL, '[]')"),
    )
    blocked: Mapped[bool] = mapped_column(
        Boolean,
        server_default=func.false(),
    )

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

    likers: Mapped[list["User"]] = relationship(
        "User",
        secondary="ItemLike",
        back_populates="liked_items",
    )

    bookmarkers: Mapped[list["User"]] = relationship(
        "User",
        secondary="ItemBookmark",
        back_populates="bookmarked_items",
    )

    loans: Mapped[list["Loan"]] = relationship(
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


class ItemImage(Base):
    __tablename__ = "item_images"

    id: Mapped[str] = mapped_column(
        str,
        primary_key=True,
    )
    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(Item.id),
    )
    item: Mapped[Item] = relationship(
        Item,
        back_populates="images",
    )


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        str,
    )

    items = relationship(
        Item,
        secondary="ItemToRegion",
        back_populates="regions",
    )


class ItemToRegion(Base):
    __tablename__ = "item_to_regions"

    item_id = mapped_column(
        Integer,
        ForeignKey(Item.id),
        primary_key=True,
    )
    region_id = mapped_column(
        Integer,
        ForeignKey(Region.id),
        primary_key=True,
    )


class ItemLike(Base):
    __tablename__ = "item_likes"

    item_id = mapped_column(
        Integer,
        ForeignKey(Item.id),
        primary_key=True,
    )
    user_id = mapped_column(
        Integer,
        ForeignKey("User.id"),
        primary_key=True,
    )


class ItemBookmark(Base):
    __tablename__ = "item_bookmarks"
    item_id = mapped_column(
        Integer,
        ForeignKey(Item.id),
        primary_key=True,
    )
    user_id = mapped_column(
        Integer,
        ForeignKey("User.id"),
        primary_key=True,
    )
