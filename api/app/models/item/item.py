from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Computed,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    and_,
    exists,
    func,
    or_,
    select,
    text,
)
from sqlalchemy.dialects.postgresql import INT4RANGE, Range
from sqlalchemy.orm import (
    Mapped,
    column_property,
    deferred,
    mapped_column,
    relationship,
)

from app.models.base import Base, CreationDate, UpdateDate
from app.models.loan import Loan

from .image import ItemImage, ItemImageAssociation
from .like import ItemLike
from .region import ItemRegionAssociation, Region

if TYPE_CHECKING:
    from app.models.user import User


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
        viewonly=True,
        lazy="raise",
    )

    # regions where the item is available
    regions: Mapped[set[Region]] = relationship(
        Region,
        secondary=ItemRegionAssociation.__tablename__,
        viewonly=True,
        lazy="raise",
    )

    # regions where the item is available
    images: Mapped[list[ItemImage]] = relationship(
        ItemImage,
        secondary=ItemImageAssociation.__tablename__,
        viewonly=True,
        lazy="raise",
        order_by=ItemImageAssociation.order,
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

    has_active_loan: Mapped[bool] = column_property(
        exists(
            select(Loan.id).where(
                and_(
                    Loan.item_id == id,
                    func.upper(Loan.during).is_not(None),
                ),
            )
        ),
    )

    available: Mapped[bool] = column_property(~or_(has_active_loan, blocked))

    first_image_name: Mapped[str] = deferred(
        column_property(
            select(ItemImageAssociation.image_name)
            .where(
                ItemImageAssociation.item_id == id,
            )
            .order_by(ItemImageAssociation.order)
            .limit(1)
            .scalar_subquery()
        ),
    )

    likes_count: Mapped[int] = deferred(
        select(func.count(ItemLike.id))
        .where(
            ItemLike.item_id == id,
        )
        .scalar_subquery(),
    )

    @property
    def region_ids(self) -> set[int]:
        return {reg.id for reg in self.regions}

    @property
    def image_names(self) -> list[str]:
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
