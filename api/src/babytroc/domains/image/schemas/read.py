from datetime import datetime

from babytroc.domains.image.schemas.base import ItemImageBase
from babytroc.shared.schemas import ReadBase


class ItemImageRead(ItemImageBase, ReadBase):
    name: str
    owner_id: int
    creation_date: datetime
