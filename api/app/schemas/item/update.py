from typing import Annotated

from pydantic import Field

from app.schemas.base import UpdateBase
from app.schemas.item.base import ItemBase

from .base import MonthRange
from .constants import DESCRIPTION_LENGTH, NAME_LENGTH


class ItemUpdate(ItemBase, UpdateBase):
    name: Annotated[
        str | None,
        Field(
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
    images: list[str] | None = None
    targeted_age_months: MonthRange | None = None
    regions: list[int] | None = None
    blocked: bool | None = None

    @property
    def as_sql_values(self):
        values = self.model_dump(
            exclude_unset=True,
            exclude={"targeted_age_months"},
        )

        if self.targeted_age_months:
            values["targeted_age_months"] = self.targeted_age_months.as_sql_range

        return values
