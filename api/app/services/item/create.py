from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.item.image import ItemImageAssociation
from app.models.item.region import ItemRegionAssociation
from app.schemas.item.create import ItemCreate
from app.schemas.item.read import ItemRead


def create_item(
    db: Session,
    owner_id: int,
    item_create: ItemCreate,
) -> ItemRead:
    """Create a new item in the database."""

    items = create_many_items(
        db=db,
        owner_ids=[owner_id],
        item_creates=[item_create],
    )

    return items[0]


def create_many_items(
    db: Session,
    owner_ids: list[int],
    item_creates: list[ItemCreate],
) -> list[ItemRead]:
    """Create many new items in the database."""

    if len(owner_ids) != len(item_creates):
        msg = "owner_id and item_create lists must be of the same length."
        raise ValueError(msg)

    # insert item
    # TODO handle constraint violations
    insert_item_stmt = (
        insert(Item)
        .values(
            [
                {
                    "owner_id": owner_id,
                    "name": item_create.name,
                    "description": item_create.description,
                    "targeted_age_months": item_create.targeted_age_months.as_sql_range,
                    "blocked": item_create.blocked,
                }
                for owner_id, item_create in zip(owner_ids, item_creates, strict=True)
            ]
        )
        .returning(Item)
    )

    # execute
    items = db.execute(insert_item_stmt).unique().scalars().all()

    # insert item regions association
    insert_item_region_stmt = insert(ItemRegionAssociation).values(
        [
            {
                "item_id": item.id,
                "region_id": region_id,
            }
            for item, item_create in zip(items, item_creates, strict=True)
            for region_id in item_create.regions
        ]
    )

    # execute
    db.execute(insert_item_region_stmt)

    # insert item_images
    # TODO handle foreign key violation
    insert_item_image_association_stmt = insert(ItemImageAssociation).values(
        [
            {
                "item_id": item.id,
                "image_name": image_name,
                "order": i,
            }
            for item, item_create in zip(items, item_creates, strict=True)
            for i, image_name in enumerate(item_create.images)
        ]
    )

    # execute
    db.execute(insert_item_image_association_stmt)

    # add stars to owner for adding an item
    # TODO add stars to owners

    return [ItemRead.model_validate(item) for item in items]
