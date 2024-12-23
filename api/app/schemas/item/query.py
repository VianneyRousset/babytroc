from typing import TYPE_CHECKING, Generic, Optional

from pydantic import Field, field_validator

from app.schemas.base import Base, ResultType

if TYPE_CHECKING:
    from app.models.item import Item


class ItemQueryFilter(Base):
    """Options on the queried page of items."""

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


class ItemQueryPageOptions(Base):
    """Options on the queried page of items."""

    limit: Optional[int] = None
    item_id_lt: Optional[int] = None
    words_match_distance_ge: Optional[float] = None
    like_id_le: Optional[int] = None
    save_id_le: Optional[int] = None


class ItemQueryPageResult(Base, Generic[ResultType]):
    """Info on the result page of items."""

    items: list[ResultType]
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

    @classmethod
    def from_orm(
        cls,
        *,
        items: list["Item"],
        words_match_distances: list[float | None],
        like_ids: list[int | None],
        save_ids: list[int | None],
        query_filter: ItemQueryFilter,
        page_options: ItemQueryPageOptions,
    ):
        return cls(
            limit=page_options.limit,
            items=items,
            words_match_distances=(
                words_match_distances if query_filter.words is not None else None
            ),
            like_ids=(like_ids if query_filter.liked_by_user_id is not None else None),
            save_ids=(save_ids if query_filter.saved_by_user_id is not None else None),
            query_filter=query_filter,
            page_options=page_options,
        )
