from collections.abc import Collection
from typing import Annotated

from pydantic import Field, field_serializer, field_validator

from app.schemas.base import CreateBase
from app.schemas.item.base import ItemBase

from .base import MonthRange
from .constants import DESCRIPTION_LENGTH, NAME_LENGTH, NAME_PATTERN


class ItemCreate(ItemBase, CreateBase):
    name: Annotated[
        str,
        Field(
            pattern=NAME_PATTERN,
            min_length=NAME_LENGTH.start,
            max_length=NAME_LENGTH.stop,
        ),
    ]
    description: Annotated[
        str,
        Field(
            min_length=DESCRIPTION_LENGTH.start,
            max_length=DESCRIPTION_LENGTH.stop,
        ),
    ]
    images: Annotated[
        list[str],
        Field(min_length=1),
    ]
    targeted_age_months: MonthRange
    regions: Annotated[
        set[int],
        Field(min_length=1),
    ]
    blocked: bool | None = False

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(
        cls,
        v: str,
    ) -> str:
        """Remove leading and trailing whitespace."""

        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(
        cls,
        v: str,
    ) -> str:
        """Remove leading and trailing whitespace."""

        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("regions", mode="before")
    @classmethod
    def validate_regions(cls, v: Collection[int]) -> set[int]:
        """Remove leading and trailing whitespace."""
        return set(v)

    @field_serializer("regions")
    @classmethod
    def serialize_regions(cls, regions: set[int]) -> list[int]:
        return sorted(regions)

    @property
    def as_sql_values(self):
        values = self.model_dump(
            exclude={"targeted_age_months"},
        )

        if self.targeted_age_months:
            values["targeted_age_months"] = self.targeted_age_months.as_sql_range

        return values
