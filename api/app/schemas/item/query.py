from typing import Annotated

from sqlalchemy import Select, and_, not_, or_
from sqlalchemy.dialects.postgresql import INT4RANGE

from app.enums import ItemQueryAvailability
from app.models.item import Item, ItemLike, ItemSave, Region
from app.schemas.base import (
    DeleteQueryFilter,
    FieldWithAlias,
    Joins,
    QueryFilter,
    ReadQueryFilter,
    StatementT,
    UpdateQueryFilter,
)
from app.schemas.query import QueryPageCursor

from .base import MonthRange


class ItemQueryFilterTargetedAgeMonths(QueryFilter):
    """Filters by targeted age months of the items query."""

    targeted_age_months: MonthRange | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(
                Item.targeted_age_months.op("&&", return_type=INT4RANGE)(
                    self.targeted_age_months.as_sql_range
                )
            )
            if self.targeted_age_months is not None
            else stmt
        )


class ItemQueryFilterRegions(QueryFilter):
    """Filters by regions of the items query."""

    regions: list[int] | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(Item.regions.any(Region.id.in_(self.regions)))
            if self.regions is not None
            else stmt
        )


class ItemQueryFilterAvailability(QueryFilter):
    """Filters by availability of the items query."""

    availability: ItemQueryAvailability | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
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

        return super()._filter(stmt)


class ItemQueryFilterOwner(QueryFilter):
    """Filters by owner of the items query."""

    owner_id: int | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(Item.owner_id == self.owner_id)
            if self.owner_id is not None
            else stmt
        )


class ItemQueryFilterLikedByUser(ReadQueryFilter):
    """Filters by liked by user of the items query."""

    liked_by_user_id: int | None = None

    @property
    def _joins(self) -> Joins:
        return super()._joins + (
            [ItemLike] if self.liked_by_user_id is not None else []
        )

    def _filter_read(self, stmt: Select) -> Select:
        return super()._filter_read(
            stmt.where(ItemLike.user_id == self.liked_by_user_id)
            if self.liked_by_user_id is not None
            else stmt
        )


class ItemQueryFilterSavedByUser(ReadQueryFilter):
    """Filters by saved by user of the items query."""

    saved_by_user_id: int | None = None

    @property
    def _joins(self) -> Joins:
        return super()._joins + (
            [ItemSave] if self.saved_by_user_id is not None else []
        )

    def _filter_read(self, stmt: Select) -> Select:
        return super()._filter_read(
            stmt.where(ItemSave.user_id == self.saved_by_user_id)
            if self.saved_by_user_id is not None
            else stmt
        )


class ItemReadQueryFilter(
    ItemQueryFilterTargetedAgeMonths,
    ItemQueryFilterRegions,
    ItemQueryFilterAvailability,
    ItemQueryFilterOwner,
    ItemQueryFilterLikedByUser,
    ItemQueryFilterSavedByUser,
    ReadQueryFilter,
):
    """Filters of the items read query."""


class ItemUpdateQueryFilter(
    ItemQueryFilterTargetedAgeMonths,
    ItemQueryFilterRegions,
    ItemQueryFilterAvailability,
    ItemQueryFilterOwner,
    UpdateQueryFilter,
):
    """Filters of the items update query."""


class ItemDeleteQueryFilter(
    ItemQueryFilterTargetedAgeMonths,
    ItemQueryFilterRegions,
    ItemQueryFilterAvailability,
    ItemQueryFilterOwner,
    DeleteQueryFilter,
):
    """Filters of the items delete query."""


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
