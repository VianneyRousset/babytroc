from sqlalchemy.orm import Session

from app import domain
from app.clients import database
from app.schemas.item.create import ItemCreate
from app.schemas.item.read import ItemRead


def create_item(
    db: Session,
    owner_id: int,
    item_create: ItemCreate,
) -> ItemRead:
    """Create a new item in the database."""

    # create item in database
    item = database.item.create_item(
        db=db,
        name=item_create.name,
        description=item_create.description,
        regions=item_create.regions,
        owner_id=owner_id,
        images=item_create.images,
        targeted_age_months=item_create.targeted_age_months,
        blocked=item_create.blocked,
    )

    # add stars to owner for adding an item
    database.user.add_stars_to_user(
        db=db,
        user=item.owner,
        count=domain.star.stars_gain_when_adding_item(1),
    )

    return ItemRead.model_validate(item)
