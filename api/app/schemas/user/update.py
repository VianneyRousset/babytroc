from typing import Optional

from pydantic import Field
from typing_extensions import Annotated

from app import config

from .base import UserBase


class UserUpdate(UserBase):
    name: Annotated[
        Optional[str],
        Field(
            min_length=config.USER_NAME_MIN_LENGTH,
            max_length=config.USER_NAME_MAX_LENGTH,
        ),
    ] = None
    avatar_seed: Annotated[
        Optional[str],
        Field(
            min_length=config.AVATAR_SEED_MIN_LENGTH,
            max_length=config.AVATAR_SEED_MAX_LENGTH,
        ),
    ] = None
