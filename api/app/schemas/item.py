from pydantic import Field, field_validator
from typing_extensions import Annotated

from app import config

from .base import Base
from .loan import LoanPreviewRead
from .region import RegionRead
from .user import UserRead


class ItemBase(Base):
    pass


class ItemCreate(ItemBase):
    owner_id: int
    name: Annotated[
        str,
        Field(
            min_length=config.ITEM_NAME_MIN_LENGTH,
            max_length=config.ITEM_NAME_MAX_LENGTH,
        ),
    ]
    description: Annotated[
        str,
        Field(
            min_length=config.ITEM_DESCRIPTION_MIN_LENGTH,
            max_length=config.ITEM_DESCRIPTION_MAX_LENGTH,
        ),
    ]
    images: list[str]
    targeted_age: list[int | None]
    regions: list[int]
    blocked: bool

    @field_validator("targeted_age")
    def validate_targeted_age(cls, v):  # noqa: N805
        if len(v) != 2:
            msg = "targeted_age must have 2 values"
            raise ValueError(msg)

        if v[0] is not None and v[1] is not None and v[0] > v[1]:
            msg = "targeted_age values must be in order"
            raise ValueError(msg)

        return v


class ItemPreviewRead(ItemBase):
    id: int
    name: str
    description: str
    images: list[str]
    targeted_age: list[int | None]
    available: bool
    liked_by_client: bool
    bookmarked_by_client: bool


class ItemRead(ItemPreviewRead):
    regions: list[RegionRead]
    owner: UserRead
    number_of_likes: int
    borrowings_from_client: list[LoanPreviewRead]
    blocked: bool | None
    loans: list[LoanPreviewRead] | None
