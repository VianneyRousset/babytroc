from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntegerIdentifier

if TYPE_CHECKING:
    from .item import Item


class Region(IntegerIdentifier, Base):
    __tablename__ = "region"

    name: Mapped[str] = mapped_column(
        String,
    )

    items: Mapped[list["Item"]] = relationship(
        "Item",
        secondary="item_region",
        back_populates="regions",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} #{self.id!r} {self.name!r}>"


class ItemRegion(Base):
    """Maps items and regions."""

    __tablename__ = "item_region"

    item_id = mapped_column(
        Integer,
        ForeignKey("item.id"),
        primary_key=True,
    )

    region_id = mapped_column(
        Integer,
        ForeignKey("region.id"),
        primary_key=True,
    )
