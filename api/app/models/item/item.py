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
from app.models.chat import Chat
from app.models.loan import Loan, LoanRequest

from .image import ItemImage
from .like import ItemLike
from .region import Region

if TYPE_CHECKING:
    from .user import User


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
        ),
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="items",
    )

    # image of the item
    images: Mapped[list[ItemImage]] = relationship(
        ItemImage,
        back_populates="item",
        cascade="all, delete-orphan",
    )

    # regions where the item is available
    regions: Mapped[list[Region]] = relationship(
        Region,
        secondary="item_region",
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

    # all active loans (should be unique or empty)
    active_loans_count: Mapped[int] = deferred(
        column_property(
            select(func.count(Loan.id))
            .where(Loan.item_id == id)
            .where(func.upper(Loan.during).is_(None))
            .scalar_subquery()
        )
    )

    # all loan requests of the item
    loan_requests: Mapped[list[LoanRequest]] = relationship(
        LoanRequest,
        back_populates="item",
        cascade="all, delete-orphan",
    )

    # number of users liking of the item
    likes_count: Mapped[int] = deferred(
        column_property(
            select(func.count(ItemLike.item_id))
            .where(ItemLike.item_id == id)
            .scalar_subquery()
        )
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
