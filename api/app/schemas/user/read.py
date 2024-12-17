from app.schemas.item import ItemPreviewRead

from .base import UserBase


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
