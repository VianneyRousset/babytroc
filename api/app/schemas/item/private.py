from typing import Union

from pydantic import field_validator
from sqlalchemy.dialects.postgresql import Range

from app.schemas.base import ReadBase
from app.schemas.item.base import ItemBase
from app.schemas.loan.read import LoanRead
from app.schemas.region.read import RegionRead
from app.schemas.user.preview import UserPreviewRead
from app.schemas.utils import integer_range_to_inclusive


class ItemPrivateRead(ItemBase, ReadBase):
    id: int
    name: str
    description: str
    targeted_age_months: tuple[int | None, int | None]
    images_names: list[str]
    available: bool
    owner_id: int

    owner: UserPreviewRead
    regions: list[RegionRead]
    likes_count: int

    blocked: bool
    loans: list[LoanRead]

    @field_validator("targeted_age_months", mode="before")
    def validate_targeted_age_months(
        cls,  # noqa: N805
        v: Union[tuple[int | None, int | None], Range],
    ) -> tuple[int | None, int | None]:
        if isinstance(v, tuple):
            return v

        v = integer_range_to_inclusive(v)
        return (v.lower, v.upper)
