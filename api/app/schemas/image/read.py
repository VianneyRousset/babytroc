from datetime import datetime

from app.models.item.image import ItemImage
from app.schemas.base import ReadBase
from app.schemas.image.base import ItemImageBase


class ItemImageRead(ItemImageBase, ReadBase):
    name: str
    order: int
    owner_id: int
    creation_date: datetime

    @classmethod
    def from_orm(cls, image: ItemImage):
        return cls.model_validate(image)
