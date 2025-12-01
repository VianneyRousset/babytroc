from collections.abc import Collection
from typing import Annotated

from pydantic import AliasChoices, Field, field_serializer, field_validator

from app.schemas.base import ReadBase
from app.schemas.item.base import ItemBase
from app.schemas.loan.read import LoanRead, LoanRequestRead
from app.schemas.user.preview import UserPreviewRead

from .base import MonthRange


class ItemRead(ItemBase, ReadBase):
    id: int
    name: str
    description: str
    targeted_age_months: MonthRange
    image_names: list[str]
    available: bool
    owner: UserPreviewRead
    region_ids: set[int]
    likes_count: int

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
    active_loan_request: Annotated[
        LoanRequestRead | None,
        Field(
            validation_alias=AliasChoices(
                "active_loan_request", "active_loan_request_from_client"
            ),
        ),
    ] = None
    active_loan: Annotated[
        LoanRead | None,
        Field(
            validation_alias=AliasChoices("active_loan", "active_loan_from_client"),
        ),
    ] = None

    # only given if owned
    blocked: bool | None = None

    @field_validator("region_ids", mode="before")
    @classmethod
    def validate_regions(cls, v: Collection[int]) -> set[int]:
        return set(v)

    @field_serializer("region_ids")
    @classmethod
    def serialize_regions(cls, region_ids: set[int]) -> list[int]:
        return sorted(region_ids)
