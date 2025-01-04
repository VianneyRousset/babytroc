from typing import Annotated, Optional

from pydantic import Field, field_validator

from app.schemas.base import UpdateBase
from app.schemas.item.base import ItemBase

from .constants import DESCRIPTION_LENGTH, NAME_LENGTH


class ItemUpdate(ItemBase, UpdateBase):
    name: Annotated[
        Optional[str],
        Field(
            min_length=NAME_LENGTH.start,
            max_length=NAME_LENGTH.stop,
        ),
    ] = None
    description: Annotated[
        Optional[str],
        Field(
            min_length=DESCRIPTION_LENGTH.start,
            max_length=DESCRIPTION_LENGTH.stop,
        ),
    ] = None
    images: Optional[list[str]] = None
    targeted_age_months: Optional[tuple[int | None, int | None]] = None
    regions: Optional[list[int]] = None
    blocked: Optional[bool] = None

    # TODO global field validator for targeted_age_months ?
    @field_validator("targeted_age_months")
    def validate_targeted_age_months(cls, v):  # noqa: N805
        if v[0] is not None and v[1] is not None and v[0] > v[1]:
            msg = "targeted_age_months values must be in order"
            raise ValueError(msg)

        return v
