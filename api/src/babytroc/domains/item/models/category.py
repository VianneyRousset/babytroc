from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from babytroc.shared.models import Base


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
