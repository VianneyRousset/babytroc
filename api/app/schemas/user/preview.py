from .base import UserBase


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
