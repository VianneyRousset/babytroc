from sqlalchemy import (
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.models.base import Base


class ItemLike(Base):
    """Maps the users and their liked items."""

    __tablename__ = "item_like"

    # the item
    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("item.id"),
        primary_key=True,
    )

    # the user liking the item
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
        primary_key=True,
    )
