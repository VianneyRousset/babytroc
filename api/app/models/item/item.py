from typing import TYPE_CHECKING, Optional

from asyncpg.types import Range
from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Identity,
    String,
    and_,
    func,
    select,
    text,
)
from sqlalchemy.dialects.postgresql import INT4RANGE
from sqlalchemy.orm import (
    Mapped,
    deferred,
    column_property,
    mapped_column,
    relationship,
)

from app.models.base import Base, CreationDate
from app.models.loan import Loan, LoanRequest

from .image import ItemImage
from .like import ItemLike
from .region import Region

if TYPE_CHECKING:
    from .user import User


class Item(CreationDate, Base):
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
    name: Mapped[str] = mapped_column(String(collation="ignore_case_and_accent"))
    description: Mapped[str] = mapped_column(String(collation="ignore_case_and_accent"))
    targeted_age: Mapped[Range] = mapped_column(
        INT4RANGE,
        server_default=text("int4range(0, NULL, '[]')"),
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

    # user that liked the item
    liked_by: Mapped[list["User"]] = relationship(
        "User",
        secondary="item_like",
        back_populates="liked_items",
    )

    # user that bookmarked the item
    bookmarked_by: Mapped[list["User"]] = relationship(
        "User",
        secondary="item_bookmark",
        back_populates="bookmarked_items",
    )

    # loans of the item
    loans: Mapped[list[Loan]] = relationship(
        Loan,
        back_populates="item",
        cascade="all, delete-orphan",
    )

    # last active loan
    active_loan: Mapped[Optional[Loan]] = deferred(
        select(Loan)
        .where(and_(Loan.id == id, func.upper_inf(Loan.during)))
        .order_by(Loan.id.desc())
        .scalar_subquery()
    )  # add .first()

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

    __table_args__ = (
        Index(
            "idx_name_description_fts",
            text("to_tsvector('french', name || ' ' || description)"),
            postgresql_using="gin",
        ),
        # Index("idx_item_name_trigram", name.ts, postgresql_using="gin_trgm_ops"),
        # Index("idx_item_description", description.collate("ignore_case_and_accent")),
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} #{self.id!r} {self.name!r}>"
