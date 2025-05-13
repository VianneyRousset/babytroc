from app.schemas.base import ReadBase

from .base import UserBase


class UserPreviewRead(UserBase, ReadBase):
    id: int
    name: str
    avatar_seed: str
