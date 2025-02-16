from typing import Optional

from pydantic import field_validator
from sqlalchemy import BooleanClauseList, Integer, Select, func
from sqlalchemy.dialects.postgresql import INT4RANGE, Range

from app.models.item import Item, ItemLike, ItemSave, Region
from app.schemas.base import QueryFilterBase


class ItemQueryFilter(QueryFilterBase):
    """Filters of the items query."""

    words: Optional[list[str]] = None
    targeted_age_months: Optional[tuple[int | None, int | None]] = None
    regions: Optional[list[int]] = None
    owner_id: Optional[int] = None
    liked_by_user_id: Optional[int] = None
    saved_by_user_id: Optional[int] = None

    @field_validator("targeted_age_months")
    def validate_targeted_age_months(cls, v):  # noqa: N805
        if v is None:
            return None

        if v[0] is not None and v[1] is not None and v[0] > v[1]:
            msg = "targeted_age_months values must be in order"
            raise ValueError(msg)

        return v

    def apply(self, stmt: Select) -> Select:
        # if words is provided, apply filtering based on words matchings
        if self.words:
            op = BooleanClauseList.or_(
                *(
                    Item.searchable_text.op("%>", return_type=Integer)(
                        func.normalize_text(self.words[0])
                    )
                    for word in self.words
                )
            )

            stmt = stmt.where(op)

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
