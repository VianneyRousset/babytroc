from babytroc.shared.schemas import ReadBase

from .base import UserBase


class UserPreviewRead(UserBase, ReadBase):
    id: int
    name: str
    avatar_seed: str
