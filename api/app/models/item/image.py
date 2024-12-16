from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Base, CreationDate

if TYPE_CHECKING:
    from .item import Item


class ItemImage(Base, CreationDate):
    """Images of items."""

    __tablename__ = "item_image"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        unique=True,
    )

    # the item
    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("item.id"),
    )
    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="images",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id!r}>"
