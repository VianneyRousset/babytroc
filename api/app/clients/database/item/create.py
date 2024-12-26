from typing import Optional

from sqlalchemy.orm import Session

from app.clients.database.user import get_user
from app.models.item import Item, ItemImage

from .region import get_region


def create_item(
    db: Session,
    *,
    name: str,
    description: str,
    targeted_age_months: list[int],
    owner_id: int,
    images: list[str],
    regions: list[int],
    blocked: Optional[bool] = False,
) -> Item:
    """Create and insert item into database."""

    item = Item(
        name=name,
        description=description,
        targeted_age_months=targeted_age_months,
        blocked=blocked,
    )

    # add images to item
    item.images.extend([ItemImage(name=name) for name in images])

    # add regions to item
    regions = [
        get_region(
            db=db,
            region_id=region_id,
        )
        for region_id in regions
    ]
    item.regions.extend(regions)

    return insert_item(
        db=db,
        item=item,
        owner_id=owner_id,
    )


def insert_item(
    db: Session,
    item: Item,
    owner_id: int,
) -> Item:
    """Insert item into the database."""

    # get the user that will be owner of the item
    owner = get_user(
        db=db,
        user_id=owner_id,
    )

    # add item to user items
    owner.items.append(item)

    db.flush()
    db.refresh(item)

    return item
