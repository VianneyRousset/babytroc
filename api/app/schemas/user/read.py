from app.schemas.base import ReadBase

from .base import UserBase


class UserRead(UserBase, ReadBase):
    id: int
    name: str
    avatar_seed: str
    stars_count: int
    likes_count: int
