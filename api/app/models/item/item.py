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
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Base, CreationDate, UpdateDate
from app.models.chat import Chat
from app.models.loan import Loan, LoanRequest

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
        back_populates="items",
        single_parent=True,
    )

    # image of the item
    images: Mapped[list[ItemImage]] = relationship(
        ItemImage,
        secondary="item_image_association",
        order_by="ItemImageAssociation.order",
        back_populates="items",
    )

    # regions where the item is available
    regions: Mapped[list[Region]] = relationship(
        Region,
        secondary="item_region_association",
        back_populates="items",
    )

    # marked as not-available
    blocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # the users that liked the item
    liked_by: Mapped[list["User"]] = relationship(
        "User",
        secondary="item_like",
        back_populates="liked_items",
    )

    # the users that saved the item
    saved_by: Mapped[list["User"]] = relationship(
        "User",
        secondary="item_save",
        back_populates="saved_items",
    )

    # loans of the item
    loans: Mapped[list[Loan]] = relationship(
        Loan,
        back_populates="item",
        cascade="all, delete-orphan",
    )

    # all loan requests of the item
    loan_requests: Mapped[list[LoanRequest]] = relationship(
        LoanRequest,
        back_populates="item",
        cascade="all, delete-orphan",
    )

    # content used for fuzzy search
    searchable_text: Mapped[str] = mapped_column(
        Computed(func.normalize_text(name + " " + description))
    )

    # chats about this item
    chats: Mapped[list[Chat]] = relationship(
        Chat,
        back_populates="item",
        cascade="all, delete-orphan",
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
