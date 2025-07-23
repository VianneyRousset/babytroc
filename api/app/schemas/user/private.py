from pydantic import EmailStr

from app.schemas.base import ReadBase
from app.schemas.item.preview import ItemPreviewRead

from .base import UserBase


class UserPrivateRead(UserBase, ReadBase):
    id: int
    validated: bool
    name: str
    email: EmailStr
    avatar_seed: str
    stars_count: int
    likes_count: int
    items: list[ItemPreviewRead]
