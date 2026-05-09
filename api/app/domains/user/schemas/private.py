from pydantic import EmailStr

from app.schemas.base import ReadBase

from .base import UserBase


class UserPrivateRead(UserBase, ReadBase):
    id: int
    validated: bool
    name: str
    email: EmailStr
    avatar_seed: str
    items_count: int
    stars_count: int
    likes_count: int
