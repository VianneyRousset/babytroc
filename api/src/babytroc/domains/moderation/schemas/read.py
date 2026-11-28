from pydantic import EmailStr

from babytroc.shared.schemas import ReadBase

from .base import ModeratorBase


class ModeratorRead(ModeratorBase, ReadBase):
    user_id: int
    name: str
    email: EmailStr
    admin: bool
