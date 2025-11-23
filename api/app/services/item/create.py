from itertools import groupby
from typing import cast

from sqlalchemy import ColumnClause, Integer, column, insert, select, values
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.star import stars_gain_when_adding_item
from app.models.item import Item
from app.models.item.image import ItemImage, ItemImageAssociation
from app.models.item.region import ItemRegionAssociation
from app.schemas.item.create import ItemCreate
from app.schemas.item.read import ItemRead
from app.services.image.read import check_images_exist
from app.services.region import get_many_regions
from app.services.user.read import get_many_users
from app.services.user.star import add_many_stars_to_users

from .read import get_many_items


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

    item_ids = await _insert_items(
        db=db,
        owner_ids=owner_ids,
        item_creates=item_creates,
    )
    await _insert_item_region_associations(
        db=db,
        item_ids=item_ids,
        item_creates=item_creates,
    )
    await _insert_item_image_associations(
        db=db,
        owner_ids=owner_ids,
        item_ids=item_ids,
        item_creates=item_creates,
    )

    # add stars to owner for adding an item
    await add_many_stars_to_users(
        db=db,
        user_ids_stars_counts={
            user_id: stars_gain_when_adding_item(len(list(group)))
            for user_id, group in groupby(owner_ids)
        },
    )

    return await get_many_items(
        db=db,
        item_ids=item_ids,
    )


async def _insert_items(
    db: AsyncSession,
    *,
    owner_ids: list[int],
    item_creates: list[ItemCreate],
) -> list[int]:
    """Insert items in database."""

    if len(owner_ids) != len(item_creates):
        msg = "owner_id and item_create lists must be of the same length."
        raise ValueError(msg)

    # insert items from values given by `owner_ids` and `item_creates`
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
        async with db.begin_nested():
            item_ids = (await db.execute(stmt)).unique().scalar().all()

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

    # Check the number of inserted items matches the number of item creates
    if len(item_ids) != len(item_creates):
        msg = (
            "The number of inserted item does not match the number of item creates. "
            "Unexpected reason"
        )
        raise RuntimeError(msg)

    return item_ids


async def _insert_item_region_associations(
    db: AsyncSession,
    *,
    item_ids: list[int],
    item_creates: list[ItemCreate],
) -> None:
    """Insert item-region associations."""

    if len(item_ids) != len(item_creates):
        msg = "item_ids and item_create lists must be of the same length."
        raise ValueError(msg)

    # insert item-region associations from values given by `item_ids` and `item_creates`
    stmt = (
        insert(ItemRegionAssociation)
        .values(
            [
                {
                    "item_id": item_id,
                    "region_id": region_id,
                }
                for item_id, item_create in zip(item_ids, item_creates, strict=True)
                for region_id in item_create.regions
            ]
        )
        .returning(ItemRegionAssociation)
    )

    # execute
    try:
        async with db.begin_nested():
            associations = (await db.execute(stmt)).unique().scalars().all()

    # If an IntegrityError is raised, it means either:
    # 1. Some regions do not exist
    # 2. Some items do not exist
    # 3. Unexpected error
    except IntegrityError as error:
        # raise RegionNotFoundError if a region does not exist (1.)
        await get_many_regions(
            db=db,
            region_ids={
                reg for item_create in item_creates for reg in item_create.regions
            },
        )

        # raise ItemNotFoundError if an item does not exist (2.)
        await get_many_items(
            db=db,
            item_ids=item_ids,
        )

        # unexpected error (3.)
        raise error

    # Check the number of inserted associations matches the total number of
    # (item_id, region_id) tuples
    if len(associations) != len(
        {
            (item_id, region_id)
            for item_id, item_create in zip(item_ids, item_creates, strict=True)
            for region_id in item_create.regions
        }
    ):
        msg = (
            "The number of inserted item-region associations does not match the number "
            "of (item_id, region_id) tuples. Unexpected reason"
        )
        raise RuntimeError(msg)


async def _insert_item_image_associations(
    db: AsyncSession,
    *,
    owner_ids: list[int],
    item_ids: list[int],
    item_creates: list[ItemCreate],
) -> None:
    """Insert item-image associations."""

    if len(owner_ids) != len(item_creates):
        msg = "owner_ids and item_create lists must be of the same length."
        raise ValueError(msg)

    if len(item_ids) != len(item_creates):
        msg = "item_ids and item_create lists must be of the same length."
        raise ValueError(msg)

    data = values(
        cast("ColumnClause[int]", ItemImageAssociation.item_id),
        column("order", Integer),
        cast("ColumnClause[str]", ItemImageAssociation.image_name),
        name="loan_request_data",
    ).data(
        [
            (item_id, i, image_name)
            for item_id, item_create in zip(item_ids, item_creates, strict=True)
            for i, image_name in enumerate(item_create.images)
        ]
    )

    # insert item-image associations from values given by `item_ids` and `item_creates`.
    # - filter images owned by the owner of the item
    stmt = (
        insert(ItemImageAssociation)
        .from_select(
            [ItemImageAssociation.item_id, ItemImageAssociation.image_name],
            select(data)
            .join(Item)
            .join(ItemImage)
            .where(Item.owner_id == ItemImage.owner_id),
        )
        .returning(ItemImageAssociation)
    )

    # execute
    try:
        async with db.begin_nested():
            associations = (await db.execute(stmt)).unique().scalars().all()

    # If an IntegrityError is raised, it means either:
    # 1. Some images do not exist
    # 2. Some images are not owned by the item owner
    # 3. Some items do not exist
    # 4. Unexpected error
    except IntegrityError as error:
        # raises ItemImageNotFound if an image does not exist or is not owned by the
        # given owner (1. and 2.)
        await check_images_exist(
            db=db,
            image_names=[
                name for item_create in item_creates for name in item_create.images
            ],
            owner_ids=[
                owner_id
                for owner_id, item_create in zip(owner_ids, item_creates, strict=True)
                for _ in item_create.images
            ],
        )
        # raises ItemNotFoundError if an item does not exist (3.)
        await get_many_items(
            db=db,
            item_ids=item_ids,
        )

        # unexpected error
        raise error

    # Check the number of inserted associations matches the total number of
    # (item_id, image_id) tuples
    if len(associations) != len(
        {
            (item_id, image_id)
            for item_id, item_create in zip(item_ids, item_creates, strict=True)
            for image_id in item_create.images
        }
    ):
        msg = (
            "The number of inserted item-image associations does not match the number "
            "of (item_id, image_id) tuples. Unexpected reason"
        )
        raise RuntimeError(msg)
