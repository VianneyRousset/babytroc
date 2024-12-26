from typing import Optional

from pydantic import Field
from typing_extensions import Annotated

from app import config
from app.schemas.base import CreateBase

from .base import UserBase


class UserCreate(UserBase, CreateBase):
    name: Annotated[
        str,
        Field(
            min_length=config.USER_NAME_MIN_LENGTH,
            max_length=config.USER_NAME_MAX_LENGTH,
        ),
    ] = None
    email: str
    password: str
    avatar_seed: Annotated[
        Optional[str],
        Field(
            min_length=config.AVATAR_SEED_MIN_LENGTH,
            max_length=config.AVATAR_SEED_MAX_LENGTH,
        ),
    ] = None
