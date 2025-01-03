from typing import Annotated, Optional

from pydantic import Field, field_validator

from app.schemas.base import CreateBase
from app.schemas.item.base import ItemBase

from .constants import DESCRIPTION_LENGTH, NAME_LENGTH


class ItemCreate(ItemBase, CreateBase):
    name: Annotated[
        str,
        Field(
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
    targeted_age_months: list[int | None]
    regions: list[int]
    blocked: Optional[bool] = False

    @field_validator("targeted_age_months")
    def validate_targeted_age_months(cls, v):  # noqa: N805
        if len(v) != 2:
            msg = "targeted_age_months must have 2 values"
            raise ValueError(msg)

        if v[0] is not None and v[1] is not None and v[0] > v[1]:
            msg = "targeted_age_months values must be in order"
            raise ValueError(msg)

        return v
