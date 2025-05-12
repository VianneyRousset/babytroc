from app.schemas.base import ReadBase
from app.schemas.item.preview import ItemPreviewRead

from .base import UserBase


class UserRead(UserBase, ReadBase):
    id: int
    name: str
    avatar_seed: str
    stars_count: int
    likes_count: int
    items: list[ItemPreviewRead]
