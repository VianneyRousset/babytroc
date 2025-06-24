from typing import Annotated

from pydantic import Field, field_validator

from app.schemas.base import CreateBase
from app.schemas.item.base import ItemBase

from .base import MonthRange
from .constants import DESCRIPTION_LENGTH, NAME_LENGTH


class ItemCreate(ItemBase, CreateBase):
    name: Annotated[
        str,
        Field(
            pattern=r"^\p{L}[\p{L} -]+\p{L}$",
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
    regions: list[int]
    blocked: bool | None = False

    @field_validator("name", mode="before")
    def validate_name(
        cls,  # noqa: N805
        v: str,
    ) -> str:
        """Remove leading and trailing whitespace."""

        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("description", mode="before")
    def validate_description(
        cls,  # noqa: N805
        v: str,
    ) -> str:
        """Remove leading and trailing whitespace."""

        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("targeted_age_months")
    def validate_targeted_age_months(cls, v):  # noqa: N805
        if v[0] is not None and v[1] is not None and v[0] > v[1]:
            msg = "targeted_age_months values must be in order"
            raise ValueError(msg)

        return v
