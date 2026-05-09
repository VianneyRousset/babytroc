from datetime import datetime

from app.domains.image.schemas.base import ItemImageBase
from app.shared.schemas import ReadBase


class ItemImageRead(ItemImageBase, ReadBase):
    name: str
    owner_id: int
    creation_date: datetime
