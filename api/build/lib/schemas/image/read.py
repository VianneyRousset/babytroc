from datetime import datetime

from app.schemas.base import ReadBase
from app.schemas.image.base import ItemImageBase


class ItemImageRead(ItemImageBase, ReadBase):
    name: str
    order: int
    owner_id: int
    creation_date: datetime
