from typing import Annotated, Optional

from pydantic import Field

from app.schemas.base import UpdateBase

from .base import UserBase
from .constants import AVATAR_SEED_LENGTH, NAME_LENGTH


class UserUpdate(UserBase, UpdateBase):
    name: Annotated[
        Optional[str],
        Field(
            min_length=NAME_LENGTH.start,
            max_length=NAME_LENGTH.stop,
        ),
    ] = None
    avatar_seed: Annotated[
        Optional[str],
        Field(
            min_length=AVATAR_SEED_LENGTH.start,
            max_length=AVATAR_SEED_LENGTH.stop,
        ),
    ] = None
