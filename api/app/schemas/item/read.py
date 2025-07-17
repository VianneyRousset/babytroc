from app.schemas.base import ReadBase
from app.schemas.item.base import ItemBase
from app.schemas.region.read import RegionRead
from app.schemas.user.preview import UserPreviewRead

from .base import MonthRange


class ItemRead(ItemBase, ReadBase):
    id: int
    name: str
    description: str
    targeted_age_months: MonthRange
    images_names: list[str]
    available: bool
    owner_id: int

    owner: UserPreviewRead
    regions: list[RegionRead]
    likes_count: int

    # only given logged in
    owned: bool | None = None
    liked: bool | None = None
    saved: bool | None = None

    # only given if owned
    blocked: bool | None = None
