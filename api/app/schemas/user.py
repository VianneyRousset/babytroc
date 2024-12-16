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

    @classmethod
    def from_orm(cls, user):
        return cls(
            id=user.id,
            name=user.name,
            avatar_seed=user.avatar_seed,
        )


class UserRead(UserPreviewRead):
    items: list["ItemPreviewRead"]
    n_stars: int
    n_likes: int

    @classmethod
    def from_orm(cls, user):
        return cls(
            id=user.id,
            name=user.name,
            avatar_seed=user.avatar_seed,
            n_stars=user.n_starts,
            n_likes=user.n_likes,
        )


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
