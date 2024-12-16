from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from .item import Item
    from .user import User


class ItemBookmark(Base):
    """Maps users and their bookmarked items."""

    __tablename__ = "item_bookmark"

    # the item
    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("item.id"),
        primary_key=True,
    )
    # the user bookmarking the item
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
        primary_key=True,
    )
