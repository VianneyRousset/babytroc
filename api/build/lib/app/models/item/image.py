from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Identity, Integer, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Base, CreationDate

if TYPE_CHECKING:
    from .item import Item


class ItemImage(Base, CreationDate):
    """Images of items.

    An incrementing integer is used as id instead of a unique name to provide a
    deterministic way to sort the image of an item.
    """

    __tablename__ = "item_image"

    name: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        unique=True,
        index=True,
    )

    order: Mapped[int] = mapped_column(
        Integer,
        Identity(
            always=True,
            start=1,
            increment=1,
        ),
    )

    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="CASCADE",
        ),
    )

    items: Mapped[set["Item"]] = relationship(
        "Item",
        secondary="item_image_association",
        back_populates="images",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name!r}>"


class ItemImageAssociation(Base):
    __tablename__ = "item_image_association"

    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "item.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    image_name: Mapped[str] = mapped_column(
        String,
        ForeignKey(
            "item_image.name",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
