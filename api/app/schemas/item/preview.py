from typing import Annotated

from pydantic import AliasChoices, Field

from app.schemas.base import ReadBase
from app.schemas.item.base import ItemBase

from .base import MonthRange


class ItemPreviewRead(ItemBase, ReadBase):
    id: int
    name: str
    targeted_age_months: MonthRange
    first_image_name: str
    available: bool
    owner_id: int

    # only given logged in
    owned: Annotated[
        bool | None,
        Field(
            validation_alias=AliasChoices("owned", "owned_by_client"),
        ),
    ] = None
    liked: Annotated[
        bool | None,
        Field(
            validation_alias=AliasChoices("liked", "liked_by_client"),
        ),
    ] = None
    saved: Annotated[
        bool | None,
        Field(
            validation_alias=AliasChoices("saved", "saved_by_client"),
        ),
    ] = None
