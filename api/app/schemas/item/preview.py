from app.schemas.item.base import ItemBase


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
