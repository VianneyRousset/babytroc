from app.schemas.item.base import ItemBase
from app.schemas.loan import LoanRead
from app.schemas.region import RegionRead
from app.schemas.user.preview import UserPreviewRead


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
