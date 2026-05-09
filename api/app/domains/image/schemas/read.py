from datetime import datetime

from app.schemas.base import ReadBase
from app.domains.image.schemas.base import ItemImageBase


class ItemImageRead(ItemImageBase, ReadBase):
    name: str
    owner_id: int
    creation_date: datetime
