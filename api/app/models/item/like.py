from sqlalchemy import (
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.models.base import Base, IntegerIdentifier


class ItemLike(IntegerIdentifier, Base):
    """Maps the users and their liked items."""

    __tablename__ = "item_like"

    # the item
    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "item.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        primary_key=True,
    )

    # the user that liked the item
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        primary_key=True,
    )

    __table_args__ = (UniqueConstraint(item_id, user_id),)
