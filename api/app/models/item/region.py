from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Identity,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from .item import Item


class Region(Base):
    __tablename__ = "region"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String,
    )

    items: Mapped[list["Item"]] = relationship(
        "Item",
        secondary="item_region_association",
        back_populates="regions",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} #{self.id!r} {self.name!r}>"


class ItemRegionAssociation(Base):
    """Items and regions association table"""

    __tablename__ = "item_region_association"

    item_id = mapped_column(
        Integer,
        ForeignKey(
            "item.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        primary_key=True,
    )

    region_id = mapped_column(
        Integer,
        ForeignKey(
            "region.id",
            onupdate="CASCADE",
        ),
        primary_key=True,
    )
