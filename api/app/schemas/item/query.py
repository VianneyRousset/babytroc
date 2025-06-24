from typing import Annotated

from pydantic import Field
from sqlalchemy import Select, and_, not_, or_
from sqlalchemy.dialects.postgresql import INT4RANGE, Range

from app.enums import ItemQueryAvailability
from app.models.item import Item, ItemLike, ItemSave, Region
from app.schemas.base import FieldWithAlias, QueryFilterBase
from app.schemas.query import QueryPageCursor

from .base import MonthRange


class ItemQueryFilter(QueryFilterBase):
    """Filters of the items query."""

    targeted_age_months: MonthRange | None = None
    regions: list[int] | None = None
    availability: ItemQueryAvailability | None = None
    owner_id: int | None = None
    liked_by_user_id: int | None = None
    saved_by_user_id: int | None = None

    def apply(self, stmt: Select) -> Select:
        # if targeted_age_months is provided, apply filtering based on range overlap
        if self.targeted_age_months is not None:
            targeted_age_months = Range(*self.targeted_age_months.range, bounds="[]")
            stmt = stmt.where(
                Item.targeted_age_months.op("&&", return_type=INT4RANGE)(
                    targeted_age_months
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
            stmt = stmt.join(ItemSave).where(ItemSave.user_id == self.saved_by_user_id)

        # if liked_by_user_id is provided, select items liked by the given user ID.
        if self.liked_by_user_id is not None:
            stmt = stmt.join(ItemLike).where(ItemLike.user_id == self.liked_by_user_id)

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
        Field(
            name="item_id",
            alias="cid",
        ),
    ] = None
