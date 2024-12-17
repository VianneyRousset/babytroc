from typing import TYPE_CHECKING, Optional

from pydantic import Field
from typing_extensions import Annotated

from app import config

from .base import Base

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


class UserRead(UserBase):
    id: int
    name: str
    avatar_seed: str
    stars_count: int
    likes_count: int
    items: list[ItemPreviewRead]

    @classmethod
    def from_orm(cls, user):
        return cls(
            id=user.id,
            name=user.name,
            avatar_seed=user.avatar_seed,
            stars_count=user.stars_count,
            likes_count=user.likes_count,
            items=[ItemPreviewRead.from_orm(item) for item in user.items],
        )


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
