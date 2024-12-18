from pydantic import Field, field_validator
from typing_extensions import Annotated

from app import config
from app.schemas.item.base import ItemBase


class ItemUpdate(ItemBase):
    name: Annotated[
        str,
        Field(
            min_length=config.ITEM_NAME_MIN_LENGTH,
            max_length=config.ITEM_NAME_MAX_LENGTH,
        ),
    ]
    description: Annotated[
        str,
        Field(
            min_length=config.ITEM_DESCRIPTION_MIN_LENGTH,
            max_length=config.ITEM_DESCRIPTION_MAX_LENGTH,
        ),
    ]
    images: list[str]
    targeted_age: list[int | None]
    regions: list[int]
    blocked: bool

    @field_validator("targeted_age")
    def validate_targeted_age(cls, v):  # noqa: N805
        if len(v) != 2:
            msg = "targeted_age must have 2 values"
            raise ValueError(msg)

        if v[0] is not None and v[1] is not None and v[0] > v[1]:
            msg = "targeted_age values must be in order"
            raise ValueError(msg)

        return v
