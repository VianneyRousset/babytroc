from typing import TYPE_CHECKING, Optional

from pydantic import Field, field_validator
from typing_extensions import Annotated

from app import config

from .base import Base

from .region import RegionRead

if TYPE_CHECKING:
    from .loan import LoanPreviewRead
    from .user import UserRead


class ItemBase(Base):
    pass


class ItemCreate(ItemBase):
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
    blocked: Optional[bool] = False

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
    owner_id: int
    name: str
    description: str
    targeted_age: list[int | None]
    images: list[str]

    @classmethod
    def from_orm(cls, item):
        return cls(
            id=item.id,
            name=item.name,
            description=item.description,
            targeted_age=[item.targeted_age.lower, item.targeted_age.upper],
            images=[img.id for img in item.images],
            owner_id=item.owner_id,
        )


class ItemRead(ItemPreviewRead):
    available: bool
    liked_by_client: bool
    bookmarked_by_client: bool
    owner: "UserRead"
    number_of_likes: int
    borrowings_from_client: list["LoanPreviewRead"]
    blocked: bool | None
    loans: list["LoanPreviewRead"] | None


class ItemUpdate(ItemBase):
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
