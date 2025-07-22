from app.schemas.base import ReadBase

from .base import UserBase


class UserRead(UserBase, ReadBase):
    id: int
    name: str
    avatar_seed: str
    items_count: int
    stars_count: int
    likes_count: int
