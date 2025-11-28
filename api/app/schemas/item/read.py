from collections.abc import Collection

from pydantic import field_serializer, field_validator

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
    images: list[str]
    available: bool
    owner: UserPreviewRead
    regions: set[int]
    likes_count: int

    # only given logged in
    owned: bool | None = None
    liked: bool | None = None
    saved: bool | None = None
    active_loan_request: LoanRequestRead | None = None
    active_loan: LoanRead | None = None

    # only given if owned
    blocked: bool | None = None

    @field_validator("regions", mode="before")
    @classmethod
    def validate_regions(cls, v: Collection[int]) -> set[int]:
        return set(v)

    @field_serializer("regions")
    @classmethod
    def serialize_regions(cls, regions: set[int]) -> list[int]:
        return sorted(regions)
