from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Computed,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import INT4RANGE, Range
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreationDate, UpdateDate

from .image import ItemImage
from .region import Region

if TYPE_CHECKING:
    from app.models.user import User

# TODO use passive_delete=True to let the db handle cascade deletions


class Item(CreationDate, UpdateDate, Base):
    __tablename__ = "item"

    # id is defined explicitly instead of using IntegerIdentifier subclassing
    # to be accessed by likes_count deferred query
    id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=True),
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    # basic infos
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    targeted_age_months: Mapped[Range[float]] = mapped_column(
        INT4RANGE,
        server_default=text("'[0,]'::int4range"),
    )

    # user owning the item
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    owner: Mapped["User"] = relationship(
        "User",
        single_parent=True,
    )

    # image of the item
    images: Mapped[list[ItemImage]] = relationship(
        ItemImage,
        secondary="item_image_association",
        order_by="ItemImageAssociation.order",
    )

    # regions where the item is available
    regions: Mapped[list[Region]] = relationship(
        Region,
        secondary="item_region_association",
    )

    # marked as not-available
    blocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # content used for fuzzy search
    searchable_text: Mapped[str] = mapped_column(
        Computed(func.normalize_text(name + " " + description))
    )

    @hybrid_property
    def first_image_name(self) -> str:
        return self.images[0].name

    @hybrid_property
    def images_names(self):
        return [img.name for img in self.images]

    __table_args__ = (
        Index(
            "idx_item_searchable_text",
            "searchable_text",
            postgresql_using="gist",
            postgresql_ops={"searchable_text": "gist_trgm_ops"},
        ),
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} #{self.id!r} {self.name!r}>"
