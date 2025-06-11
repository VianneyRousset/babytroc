from pydantic import EmailStr

from app.schemas.base import ReadBase
from app.schemas.item.preview import ItemPreviewRead

from .base import UserBase


class UserPrivateRead(UserBase, ReadBase):
    id: int
    name: str
    email: EmailStr
    avatar_seed: str
    stars_count: int
    likes_count: int
    items: list[ItemPreviewRead]
