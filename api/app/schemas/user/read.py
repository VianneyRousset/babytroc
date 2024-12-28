from app.schemas.base import ReadBase

from .base import UserBase


class UserRead(UserBase, ReadBase):
    id: int
    name: str
    avatar_seed: str
    stars_count: int
    likes_count: int

    @classmethod
    def from_orm(cls, user):
        return cls(
            id=user.id,
            name=user.name,
            avatar_seed=user.avatar_seed,
            stars_count=user.stars_count,
            likes_count=user.likes_count,
        )
