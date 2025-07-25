from typing import Annotated, TypeVar

from sqlalchemy import Delete, Select, Update, and_, not_, or_
from sqlalchemy.dialects.postgresql import INT4RANGE

from app.enums import ItemQueryAvailability
from app.models.item import Item, ItemLike, ItemSave, Region
from app.schemas.base import FieldWithAlias, QueryFilterBase
from app.schemas.query import QueryPageCursor

from .base import MonthRange

T = TypeVar("T", Select, Update, Delete)


class ItemQueryFilter(QueryFilterBase):
    """Filters of the items query."""

    targeted_age_months: MonthRange | None = None
    regions: list[int] | None = None
    availability: ItemQueryAvailability | None = None
    owner_id: int | None = None
    liked_by_user_id: int | None = None
    saved_by_user_id: int | None = None

    def apply(self, stmt: T) -> T:
        # if targeted_age_months is provided, apply filtering based on range overlap
        if self.targeted_age_months is not None:
            stmt = stmt.where(
                Item.targeted_age_months.op("&&", return_type=INT4RANGE)(
                    self.targeted_age_months.as_sql_range
                )
            )

        # if regions is provided, select items in the given regions
        if self.regions is not None:
            stmt = stmt.where(Item.regions.any(Region.id.in_(self.regions)))

        # if available is provided, filter by availability
        if self.availability is not None:
            match self.availability:
                case ItemQueryAvailability.yes:
                    stmt = stmt.where(
                        and_(
                            not_(Item.blocked),
                            Item.active_loans_count == 0,
                        )
                    )
                case ItemQueryAvailability.no:
                    stmt = stmt.where(
                        or_(
                            Item.blocked,
                            Item.active_loans_count > 0,
                        )
                    )

        # if owner_id is provide, select items where owner_id is the given ID.
        if self.owner_id is not None:
            stmt = stmt.where(Item.owner_id == self.owner_id)

        # if saved_by_user_id is provided, select items saved by the given user ID.
        if self.saved_by_user_id is not None:
            if isinstance(stmt, Update):
                msg = "Cannot apply saved_by_user_id filtering on Update statement"
                raise TypeError(msg)

            stmt = stmt.join(ItemSave)
            stmt = stmt.where(ItemSave.user_id == self.saved_by_user_id)

        # if liked_by_user_id is provided, select items liked by the given user ID.
        if self.liked_by_user_id is not None:
            if isinstance(stmt, Update):
                msg = "Cannot apply liked_by_user_id filtering on Update statement"
                raise TypeError(msg)
            stmt = stmt.join(ItemLike)
            stmt = stmt.where(ItemLike.user_id == self.liked_by_user_id)

        return stmt


class ItemQueryPageCursor(QueryPageCursor):
    item_id: Annotated[
        int | None,
        FieldWithAlias(
            name="item_id",
            alias="cid",
        ),
    ] = None


class ItemMatchingWordsQueryPageCursor(QueryPageCursor):
    words_match: Annotated[
        int | None,
        FieldWithAlias(
            name="words_match",
            alias="cwm",
        ),
    ] = None
    item_id: Annotated[
        int | None,
        FieldWithAlias(
            name="item_id",
            alias="cid",
        ),
    ] = None
