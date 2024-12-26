from typing import Generic, Optional

from pydantic import field_validator
from sqlalchemy import Integer, Select, func
from sqlalchemy.dialects.postgresql import INT4RANGE, Range

from app.models.item import Item, ItemLike, ItemSave, Region
from app.schemas.base import (
    QueryFilterBase,
    QueryPageOptionsBase,
    QueryPageResultBase,
    ResultType,
)


class ItemQueryFilter(QueryFilterBase):
    """Filters of the items query."""

    words: Optional[list[str]] = None
    targeted_age_months: Optional[list[int]] = None
    regions: Optional[list[int]] = None
    owner_id: Optional[int] = None
    liked_by_user_id: Optional[int] = None
    saved_by_user_id: Optional[int] = None

    @field_validator("targeted_age_months")
    def validate_targeted_age_months(cls, v):  # noqa: N805
        if v is None:
            return None

        if len(v) != 2:
            msg = "targeted_age_months must have 2 values"
            raise ValueError(msg)

        if v[0] is not None and v[1] is not None and v[0] > v[1]:
            msg = "targeted_age_months values must be in order"
            raise ValueError(msg)

    def apply(self, stmt: Select) -> Select:
        # if words is provided, apply filtering based on words matchings
        if self.words is not None:
            for word in self.words:
                stmt = stmt.where(
                    Item.searchable_text.op("%>", return_type=Integer)(
                        func.normalize_text(word)
                    )
                )

        # if targeted_age_months is provided, apply filtering based on range overlap
        if self.targeted_age_months is not None:
            targeted_age_months = Range(*self.targeted_age_months, bounds="[]")
            stmt = stmt.where(
                Item.targeted_age_months.op("&&", return_type=INT4RANGE)(
                    targeted_age_months
                )
            )

        # if regions is provided, select items in the given regions
        if self.regions is not None:
            stmt = stmt.where(Item.regions.any(Region.id.in_(self.regions)))

        # if owner_id is provide, select items where owner_id is the given ID.
        if self.owner_id is not None:
            stmt = stmt.where(Item.owner_id == self.owner_id)

        # if saved_by_user_id is provided, select items saved by the given user ID.
        # TODO should use right join ?
        if self.saved_by_user_id is not None:
            stmt = stmt.join(ItemSave).where(ItemSave.user_id == self.saved_by_user_id)

        # if liked_by_user_id is provided, select items liked by the given user ID.
        if self.liked_by_user_id is not None:
            stmt = stmt.join(ItemLike).where(ItemLike.user_id == self.liked_by_user_id)

        return stmt


class ItemQueryPageOptions(QueryPageOptionsBase):
    """Options on the queried page of items."""

    limit: Optional[int] = None
    item_id_lt: Optional[int] = None
    words_match_distance_ge: Optional[float] = None
    like_id_le: Optional[int] = None
    save_id_le: Optional[int] = None

    def apply(self, stmt: Select, *, words_match_distance) -> Select:
        # if limit is provided, limit number of results
        if self.limit is not None:
            stmt = stmt.limit(self.limit)

        # if item_id_lt is provided, select the item with ID less than the given value
        if self.item_id_lt is not None:
            stmt = stmt.where(Item.id < self.item_id_lt)

        # if words_match_distance_ge is provided, select items with words match distance
        # greater or equal to the given value
        if self.words_match_distance_ge is not None:
            stmt = stmt.where(words_match_distance >= self.words_match_distance_ge)

        # if like_id_le is provided, having a like with like_id less or equal
        # to the given value.
        if self.like_id_le is not None:
            stmt = stmt.where(ItemLike.id <= self.like_id_le)

        # if save_id_le is provided, having a save with save_id less or equal
        # to the given value.
        if self.save_id_le is not None:
            stmt = stmt.where(ItemSave.id <= self.save_id_le)

        return stmt


class ItemQueryPageResult(QueryPageResultBase, Generic[ResultType]):
    """Info on the result page of items."""

    words_match_distances: Optional[list[float]] = None
    like_ids: Optional[list[int]] = None
    save_ids: Optional[list[int]] = None

    query_filter: ItemQueryFilter
    page_options: ItemQueryPageOptions

    @property
    def max_words_match_distance(self) -> float | None:
        if self.words_match_distances:
            return max(self.words_match_distances)
        return None

    @property
    def min_item_id(self) -> int | None:
        if self.items:
            return min(item.id for item in self.result)
        return None

    @property
    def min_like_id(self) -> int | None:
        if self.like_ids:
            return min(self.like_ids)
        return None

    @property
    def min_save_id(self) -> int | None:
        if self.save_ids:
            return min(self.save_ids)
        return None
