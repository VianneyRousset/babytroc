
from pydantic import field_validator
from sqlalchemy.dialects.postgresql import Range

from app.schemas.base import ReadBase
from app.schemas.item.base import ItemBase
from app.schemas.utils import integer_range_to_inclusive


class ItemPreviewRead(ItemBase, ReadBase):
    id: int
    name: str
    targeted_age_months: tuple[int | None, int | None]
    first_image_name: str
    available: bool
    owner_id: int

    @field_validator("targeted_age_months", mode="before")
    def validate_targeted_age_months(
        cls,  # noqa: N805
        v: tuple[int | None, int | None] | Range,
    ) -> tuple[int | None, int | None]:
        if isinstance(v, tuple):
            return v

        v = integer_range_to_inclusive(v)
        return (v.lower, v.upper)
