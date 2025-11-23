from itertools import groupby

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from app.services.region import get_many_regions
from sqlalchemy.orm import AsyncSession
from app.services.user.read import get_many_users

from app.services.region import list_regions
from app.domain.star import stars_gain_when_adding_item
from app.errors.image import ItemImageNotFoundError
from app.errors.region import RegionNotFoundError
from app.errors.user import UserNotFoundError
from app.models.item import Item
from app.models.item.image import ItemImageAssociation
from app.models.item.region import ItemRegionAssociation
from app.schemas.item.create import ItemCreate
from app.schemas.item.read import ItemRead
from app.services.user.star import add_stars_to_user


async def create_item(
    db: AsyncSession,
    owner_id: int,
    item_create: ItemCreate,
) -> ItemRead:
    """Create a new item in the database."""

    items = await create_many_items(
        db=db,
        owner_ids=[owner_id],
        item_creates=[item_create],
    )

    return items[0]


async def create_many_items(
    db: AsyncSession,
    owner_ids: list[int],
    item_creates: list[ItemCreate],
) -> list[ItemRead]:
    """Create many new items in the database."""

    items = await _insert_items(
        db=db,
        owner_ids=owner_ids,
        item_creates=item_creates,
    )
    await _insert_item_region_associations()
    await _insert_item_image_associations()

    return get_many_items()


async def _insert_items(
    db: AsyncSession,
    owner_ids: list[int],
    item_creates: list[ItemCreate],
) -> list[int]:
    """Insert items in database."""

    if len(owner_ids) != len(item_creates):
        msg = "owner_id and item_create lists must be of the same length."
        raise ValueError(msg)

    # insert from values given by `item_creates`
    stmt = (
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
        .returning(Item.id)
    )

    # execute
    try:
        with db.begin_nested():
            item_ids = db.execute(stmt).unique().scalars().all()

    # If an IntegrityError is raised, it means either:
    # 1. The owner does not exist
    # 2. Unexpected error
    except IntegrityError as error:
        # raises UserNotFoundError if any owner does not exist (1.)
        await get_many_users(
            db=db,
            user_ids=set(owner_ids),
        )

        # unexpected error (2.)
        raise error

    return item_ids


def _insert_item_region_associations(
    db: AsyncSession,
    item_ids: list[int],
    item_creates: list[ItemCreate],
) -> None:
    """Insert item-region associations."""

    if len(item_ids) != len(item_creates):
        msg = "item_ids and item_create lists must be of the same length."
        raise ValueError(msg)

    # insert item-region association
    stmt = insert(ItemRegionAssociation).values(
        [
            {
                "item_id": item_id,
                "region_id": region_id,
            }
            for item_id, item_create in zip(item_ids, item_creates, strict=True)
            for region_id in item_create.regions
        ]
    )

    # execute
    try:
        db.execute(stmt)

    # If an IntegrityError is raised, it means either:
    # 1. The regions does not exist
    # 2. Unexpected error
    except IntegrityError as error:
        # raise RegionNotFoundError if a region is missing
        await get_many_regions(
            db=db,
            regions_ids={
                reg for item_create in item_creates for reg in item_create.regions
            },
        )

    # TODO check all images are owned by the user

    # insert item-image associations
    insert_item_image_associations_stmt = insert(ItemImageAssociation).values(
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
    try:
        db.execute(insert_item_image_associations_stmt)

    except IntegrityError as error:
        raise ItemImageNotFoundError(
            {
                "name": [
                    image_name
                    for item_create in item_creates
                    for image_name in item_create.images
                ]
            }
        ) from error

    # add stars to owner for adding an item
    for owner_id, group in groupby(owner_ids):
        add_stars_to_user(
            db=db,
            user_id=owner_id,
            count=stars_gain_when_adding_item(len(list(group))),
        )

    return [ItemRead.model_validate(item) for item in items]
