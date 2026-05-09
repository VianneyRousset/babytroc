from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Category(Base):
    __tablename__ = "category"

    slug: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String)

    parent_slug: Mapped[str | None] = mapped_column(
        String,
        ForeignKey(
            "category.slug",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.slug!r} {self.name!r}>"


class ItemCategoryAssociation(Base):
    __tablename__ = "item_category_association"

    item_id: Mapped[int] = mapped_column(
        ForeignKey(
            "item.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        primary_key=True,
    )

    category_slug: Mapped[str] = mapped_column(
        String,
        ForeignKey(
            "category.slug",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        primary_key=True,
    )
