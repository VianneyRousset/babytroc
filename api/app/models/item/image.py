from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreationDate


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

    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
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
            onupdate="CASCADE",
        ),
        primary_key=True,
    )

    image_name: Mapped[str] = mapped_column(
        String,
        ForeignKey(
            "item_image.name",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        primary_key=True,
    )

    order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
