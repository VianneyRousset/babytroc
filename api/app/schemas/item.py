from typing import Optional, TYPE_CHECKING

from pydantic import Field, field_validator
from typing_extensions import Annotated

from app import config

from .base import Base
from .loan import LoanRead

from app.schemas.user.preview import UserPreviewRead
from app.schemas.region import RegionRead

if TYPE_CHECKING:
    from app.schemas.user.preview import UserRead


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
    name: str
    description: str
    targeted_age: list[int | None]
    images: list[str]
    available: bool
    owner_id: int

    @classmethod
    def from_orm(cls, item):
        return cls(
            id=item.id,
            name=item.name,
            description=item.description,
            targeted_age=[item.targeted_age.lower, item.targeted_age.upper],
            images=[img.id for img in item.images],
            available=True,
            owner_id=item.owner_id,
        )


class ItemRead(ItemBase):
    id: int
    name: str
    description: str
    targeted_age: list[int | None]
    images: list[str]
    available: bool
    owner_id: int

    owner: UserPreviewRead
    regions: list[RegionRead]
    likes_count: int

    @classmethod
    def from_orm(cls, item):
        return cls(
            id=item.id,
            name=item.name,
            description=item.description,
            targeted_age=[item.targeted_age.lower, item.targeted_age.upper],
            images=[img.id for img in item.images],
            available=True,
            owner_id=item.owner_id,
            owner=UserPreviewRead.from_orm(item.owner),
            regions=[RegionRead.from_orm(region) for region in item.regions],
            likes_count=item.likes_count,
        )


class ItemPrivateRead(ItemBase):
    id: int
    name: str
    description: str
    targeted_age: list[int | None]
    images: list[str]
    available: bool
    owner_id: int

    owner: UserPreviewRead
    regions: list[RegionRead]
    likes_count: int

    blocked: bool
    loans: list[LoanRead]

    @classmethod
    def from_orm(cls, item):
        return cls(
            id=item.id,
            name=item.name,
            description=item.description,
            targeted_age=[item.targeted_age.lower, item.targeted_age.upper],
            images=[img.id for img in item.images],
            available=True,
            owner_id=item.owner_id,
            owner=UserPreviewRead.from_orm(item.owner),
            regions=[RegionRead.from_orm(region) for region in item.regions],
            likes_count=item.likes_count,
            blocked=item.blocked,
            loans=[LoanRead.from_orm(loan) for loan in item.loans],
        )


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
