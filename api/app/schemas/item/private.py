from app.schemas.base import ReadBase
from app.schemas.item.base import ItemBase
from app.schemas.loan.read import LoanRead
from app.schemas.region.read import RegionRead
from app.schemas.user.preview import UserPreviewRead

from .base import MonthRange


class ItemPrivateRead(ItemBase, ReadBase):
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

    blocked: bool
    loans: list[LoanRead]
