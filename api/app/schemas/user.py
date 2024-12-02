from typing import TYPE_CHECKING

from pydantic import Field
from typing_extensions import Annotated

from app import config

from .base import Base

if TYPE_CHECKING:
    from .item import ItemPreviewRead


class UserBase(Base):
    pass


class UserPreviewRead(UserBase):
    id: int
    name: str
    avatar_seed: str
    n_stars: int
    n_likes: int


class UserRead(UserPreviewRead):
    items: list["ItemPreviewRead"]


class UserUpdate(UserBase):
    name: Annotated[
        str,
        Field(
            min_length=config.USER_NAME_MIN_LENGTH,
            max_length=config.USER_NAME_MAX_LENGTH,
        ),
    ]
    avatar_seed: Annotated[
        str,
        Field(
            min_length=config.AVATAR_SEED_MIN_LENGTH,
            max_length=config.AVATAR_SEED_MAX_LENGTH,
        ),
    ]
