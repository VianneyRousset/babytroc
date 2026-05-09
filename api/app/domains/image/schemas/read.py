from datetime import datetime

from app.shared.schemas import ReadBase
from app.domains.image.schemas.base import ItemImageBase


class ItemImageRead(ItemImageBase, ReadBase):
    name: str
    owner_id: int
    creation_date: datetime
