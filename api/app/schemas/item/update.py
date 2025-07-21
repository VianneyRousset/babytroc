from typing import Annotated

from pydantic import Field

from app.schemas.base import UpdateBase
from app.schemas.item.base import ItemBase

from .base import MonthRange
from .constants import DESCRIPTION_LENGTH, NAME_LENGTH, NAME_PATTERN


class ItemUpdate(ItemBase, UpdateBase):
    name: Annotated[
        str | None,
        Field(
            pattern=NAME_PATTERN,
            min_length=NAME_LENGTH.start,
            max_length=NAME_LENGTH.stop,
        ),
    ] = None
    description: Annotated[
        str | None,
        Field(
            min_length=DESCRIPTION_LENGTH.start,
            max_length=DESCRIPTION_LENGTH.stop,
        ),
    ] = None
    images: Annotated[
        list[str] | None,
        Field(min_length=1),
    ] = None
    targeted_age_months: MonthRange | None = None
    regions: Annotated[
        list[int] | None,
        Field(min_length=1),
    ] = None
    blocked: bool | None = False

    def as_sql_values(self, *, exclude=None):
        exclude = exclude or {}

        values = self.model_dump(
            exclude_unset=True,
            exclude={"targeted_age_months", *exclude},
        )

        if self.targeted_age_months:
            values["targeted_age_months"] = self.targeted_age_months.as_sql_range

        return values
