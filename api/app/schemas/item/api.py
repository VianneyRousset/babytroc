from typing import Optional

from pydantic import Field

from app.schemas.base import ApiQueryBase


class ItemApiQuery(ApiQueryBase):
    # words
    q: Optional[list[str]] = Field(
        title="Words used for fuzzy search",
        description=(
            "An item is returned if any word in this list fuzzy-matches a word in the "
            "item's name or description. However, the more given words that do not "
            "match any word in the item's name or description, the higher the word "
            "matching distance is."
        ),
        examples=[
            ["chair"],
            ["dog", "cat"],
        ],
        default=None,
    )

    # targeted_age_months
    mo: Optional[list[int | None]] = Field(
        title="Targeted age months",
        description=(
            "An item is returned if its targeted age months is included in this range. "
            "The values are the targeted age in months. A null value specify "
            "an infinite bound."
        ),
        examples=[
            [3, 12],
            [8, None],
        ],
        default=None,
    )

    # regions
    reg: Optional[list[int]] = Field(
        title="Regions",
        description=(
            "An item is returned if it is available in any of these regions IDs."
        ),
        examples=[
            [4],
            [2, 4, 7, 8],
        ],
        default=None,
    )

    # limit
    n: Optional[int] = Field(
        title="Limit returned items count",
        description="Limit the number of items returned.",
        examples=[
            [42],
        ],
        gt=0,
        le=128,
        default=64,
    )

    # cursor item_id
    cid: Optional[int] = Field(
        title="Page cursor for item ID",
        gt=0,
        default=None,
    )

    # cursor words_match
    cwm: Optional[int] = Field(
        title="Page cursor for words match",
        le=0,
        default=None,
    )
