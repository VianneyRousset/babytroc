from pydantic import Field, field_validator

from app.enums import ItemQueryAvailability
from app.schemas.base import ApiQueryBase


class ItemApiQueryBase(ApiQueryBase):
    # words
    q: list[str] | None = Field(
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
    mo: str | None = Field(
        alias="mo",
        title="Targeted age months",
        description=(
            "An item is returned if its targeted age months is included in this range. "
            "The values are the targeted age in months. A null value specify "
            "an infinite bound."
        ),
        examples=[
            "3-12",
            "8-",
        ],
        default=None,
        pattern=r"^\d*-\d*$",
    )

    # availability
    av: ItemQueryAvailability | None = Field(
        title="Availability",
        default=ItemQueryAvailability.yes,
    )

    @field_validator("mo")
    def validate_mo(cls, mo: str):  # noqa: N805
        lower, upper = cls.parse_mo(mo)

        if lower is not None and upper is not None and lower > upper:
            msg = "mo values must be in order"
            raise ValueError(msg)

        return mo

    @staticmethod
    def parse_mo(mo: str) -> tuple[int | None, int | None]:
        try:
            lower_str, upper_str = mo.split("-")

        except ValueError as error:
            msg = "mo must have 2 values"
            raise ValueError(msg) from error

        lower = int(lower_str) if lower_str else None
        upper = int(upper_str) if upper_str else None

        return lower, upper

    @property
    def parsed_mo(self) -> tuple[int | None, int | None] | None:
        if self.mo is None:
            return None

        return self.parse_mo(self.mo)

    # regions
    reg: list[int] | None = Field(
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


class ItemApiQuery(ItemApiQueryBase):
    # limit
    n: int | None = Field(
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
    cid: int | None = Field(
        title="Page cursor for item ID",
        gt=0,
        default=None,
    )

    # cursor words_match
    cwm: int | None = Field(
        title="Page cursor for words match",
        le=0,
        default=None,
    )


class SavedItemApiQuery(ItemApiQueryBase):
    pass


class LikedItemApiQuery(ItemApiQueryBase):
    pass
