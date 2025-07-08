from typing import Annotated

from app.enums import ItemQueryAvailability
from app.schemas.base import ApiQueryBase, FieldWithAlias, PageLimitField
from app.schemas.query import QueryPageOptions

from .base import MonthRange
from .query import (
    ItemMatchingWordsQueryPageCursor,
    ItemQueryFilter,
    ItemQueryPageCursor,
)


class ItemApiQueryBase(ApiQueryBase):
    # words
    words: Annotated[
        list[str] | None,
        FieldWithAlias(
            name="words",
            alias="q",
            title="Words used for fuzzy search",
            description=(
                "An item is returned if any word in this list fuzzy-matches a word in "
                "the item's name or description. However, the more given words that do "
                "not match any word in the item's name or description, the higher the "
                "word matching distance is."
            ),
            examples=[
                ["chair"],
                ["dog", "cat"],
            ],
        ),
    ] = None

    # targeted_age_months
    targeted_age_months: Annotated[
        MonthRange | None,
        FieldWithAlias(
            name="targeted_age_months",
            alias="mo",
            title="Targeted age months",
            description=(
                "An item is returned if its targeted age months is included in this "
                "range. The values are the targeted age in months. A null value "
                "specify an infinite bound."
            ),
            examples=[
                "3-12",
                "8-",
            ],
        ),
    ] = None

    # availability
    availability: Annotated[
        ItemQueryAvailability | None,
        FieldWithAlias(
            name="availability",
            alias="av",
            title="Availability",
        ),
    ] = None

    # regions
    regions: Annotated[
        list[int] | None,
        FieldWithAlias(
            name="regions",
            alias="reg",
            title="Regions",
            description=(
                "An item is returned if it is available in any of these regions IDs."
            ),
            examples=[
                [4],
                [2, 4, 7, 8],
            ],
        ),
    ] = None

    limit: Annotated[int | None, PageLimitField()] = None


class ItemApiQuery(ItemApiQueryBase, ItemMatchingWordsQueryPageCursor):
    @property
    def item_query_filter(self) -> ItemQueryFilter:
        return ItemQueryFilter(
            targeted_age_months=self.targeted_age_months,
            regions=self.regions,
            availability=self.availability,
        )

    @property
    def item_query_page_cursor(self) -> ItemQueryPageCursor:
        return ItemQueryPageCursor(
            item_id=self.item_id,
        )

    @property
    def item_matching_words_query_page_cursor(self) -> ItemMatchingWordsQueryPageCursor:
        return ItemMatchingWordsQueryPageCursor(
            item_id=self.item_id,
            words_match=self.words_match,
        )

    @property
    def item_query_page_options(self) -> QueryPageOptions[ItemQueryPageCursor]:
        return QueryPageOptions[ItemQueryPageCursor](
            limit=self.limit,
            cursor=self.item_query_page_cursor,
        )

    @property
    def item_matching_words_query_page_options(
        self,
    ) -> QueryPageOptions[ItemMatchingWordsQueryPageCursor]:
        return QueryPageOptions[ItemMatchingWordsQueryPageCursor](
            limit=self.limit,
            cursor=self.item_matching_words_query_page_cursor,
        )


class SavedItemApiQuery(ItemApiQuery):
    pass


class LikedItemApiQuery(ItemApiQuery):
    pass
