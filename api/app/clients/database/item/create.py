from sqlalchemy.orm import Session

from app.clients.database.region import get_region
from app.clients.database.user import get_user
from app.models.item import Item
from app.models.item.image import ItemImageAssociation
from app.schemas.item.base import MonthRange


def create_item(
    db: Session,
    *,
    name: str,
    description: str,
    targeted_age_months: MonthRange,
    owner_id: int,
    images: list[str],
    regions: list[int],
    blocked: bool | None = False,
) -> Item:
    """Create and insert item into database."""

    # check owner exists
    owner = get_user(
        db=db,
        user_id=owner_id,
    )

    item = Item(
        name=name,
        description=description,
        targeted_age_months=targeted_age_months.as_sql_range,
        blocked=blocked,
        owner_id=owner.id,
    )

    db.add(item)
    db.flush()
    db.refresh(item)

    # add item-image associations
    for i, name in enumerate(images):
        association = ItemImageAssociation(
            item_id=item.id,
            image_name=name,
            order=i,
        )
        db.add(association)

    # add regions to item
    for region_id in regions:
        region = get_region(db, region_id)
        region.items.append(item)

    db.add(item)
    db.flush()
    db.refresh(item)

    return item
