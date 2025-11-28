from app.schemas.base import ReadBase
from app.schemas.item.base import ItemBase

from .base import MonthRange


class ItemPreviewRead(ItemBase, ReadBase):
    id: int
    name: str
    targeted_age_months: MonthRange
    first_image: str
    available: bool
    owner_id: int

    # only given logged in
    liked: bool | None = None
    saved: bool | None = None
    owned: bool | None = None
