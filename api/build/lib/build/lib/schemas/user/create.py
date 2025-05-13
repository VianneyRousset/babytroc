from typing import Annotated

from pydantic import Field

from app.schemas.base import CreateBase

from .base import UserBase
from .constants import AVATAR_SEED_LENGTH, NAME_LENGTH


class UserCreate(UserBase, CreateBase):
    name: Annotated[
        str,
        Field(
            min_length=NAME_LENGTH.start,
            max_length=NAME_LENGTH.stop,
        ),
    ]
    email: str
    password: str
    avatar_seed: Annotated[
        str | None,
        Field(
            min_length=AVATAR_SEED_LENGTH.start,
            max_length=AVATAR_SEED_LENGTH.stop,
        ),
    ] = None
