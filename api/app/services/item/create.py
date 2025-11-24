from itertools import groupby
from typing import Self, cast

from sqlalchemy import ColumnClause, Integer, column, insert, select, values
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.star import stars_gain_when_adding_item
from app.models.item import Item
from app.models.item.image import ItemImage, ItemImageAssociation
from app.models.item.region import ItemRegionAssociation
from app.schemas.base import Base as SchemaBase
from app.schemas.item.create import ItemCreate
from app.schemas.item.read import ItemRead
from app.services.image.read import CheckImageOwner, check_image_owners, get_many_images
from app.services.region import get_many_regions
from app.services.user.read import get_many_users
from app.services.user.star import AddUserStars, add_many_stars_to_users

from .read import get_many_items


class CreateItem(SchemaBase):
    owner_id: int
    item_create: ItemCreate


class InsertItemRegionAssociation(SchemaBase):
    item_id: int
    region_id: int

    @classmethod
    def from_item_regions(
        cls,
        item_id: int,
        region_ids: set[int],
    ) -> list[Self]:
        return [
            cls(
                item_id=item_id,
                region_id=region_id,
            )
            for region_id in region_ids
        ]


class InsertItemImageAssociation(SchemaBase):
    item_id: int
    owner_id: int
    order: int
    image_name: str

    @classmethod
    def from_item_images(
        cls,
        *,
        item_id: int,
        owner_id: int,
        image_names: list[str],
    ) -> list[Self]:
        return [
            cls(
                item_id=item_id,
                owner_id=owner_id,
                order=i,
                image_name=image_name,
            )
            for i, image_name in enumerate(image_names)
        ]


async def create_item(
    db: AsyncSession,
    owner_id: int,
    item_create: ItemCreate,
) -> ItemRead:
    """Create a new item in the database."""

    items = await create_many_items(
        db=db,
        items=[
            CreateItem(
                owner_id=owner_id,
                item_create=item_create,
            )
        ],
    )

    return items[0]


async def create_many_items(
    db: AsyncSession,
    items: list[CreateItem],
) -> list[ItemRead]:
    """Create many new items in the database."""

    item_ids = await _insert_items(
        db=db,
        items=items,
    )
    await _insert_item_region_associations(
        db=db,
        associations=[
            association
            for item_id, item in zip(item_ids, items, strict=True)
            for association in InsertItemRegionAssociation.from_item_regions(
                item_id=item_id,
                region_ids=item.item_create.regions,
            )
        ],
    )
    await _insert_item_image_associations(
        db=db,
        associations=[
            association
            for item_id, item in zip(item_ids, items, strict=True)
            for association in InsertItemImageAssociation.from_item_images(
                item_id=item_id,
                owner_id=item.owner_id,
                image_names=item.item_create.images,
            )
        ],
    )

    # add stars to owner for adding an item
    await add_many_stars_to_users(
        db=db,
        stars=[
            AddUserStars(
                user_id=user_id,
                stars_count=stars_gain_when_adding_item(len(list(group))),
            )
            for user_id, group in groupby([item.owner_id for item in items])
        ],
    )

    return await get_many_items(
        db=db,
        item_ids=set(item_ids),
    )


async def _insert_items(
    db: AsyncSession,
    items: list[CreateItem],
) -> list[int]:
    """Insert items in database."""

    # insert items from values given by `owner_ids` and `item_creates`
    stmt = (
        insert(Item)
        .values(
            [
                {
                    "owner_id": item.owner_id,
                    "name": item.item_create.name,
                    "description": item.item_create.description,
                    "targeted_age_months": (
                        item.item_create.targeted_age_months.as_sql_range
                    ),
                    "blocked": item.item_create.blocked,
                }
                for item in items
            ]
        )
        .returning(Item.id)
    )

    # execute
    try:
        async with db.begin_nested():
            item_ids: list[int] = list(
                (await db.execute(stmt)).unique().scalars().all()
            )

    # If an IntegrityError is raised, it means either:
    # 1. The owner does not exist
    # 2. Unexpected error
    except IntegrityError as error:
        # raises UserNotFoundError if any owner does not exist (1.)
        await get_many_users(
            db=db,
            user_ids={item.owner_id for item in items},
        )

        # unexpected error (2.)
        raise error

    # Check the number of inserted items matches the number of item creates
    if len(item_ids) != len(items):
        msg = (
            "The number of inserted item does not match the number of item creates. "
            "Unexpected reason"
        )
        raise RuntimeError(msg)

    return item_ids


async def _insert_item_region_associations(
    db: AsyncSession,
    associations: list[InsertItemRegionAssociation],
) -> None:
    """Insert item-region associations."""

    # insert item-region associations from values given by `item_ids` and `item_creates`
    stmt = (
        insert(ItemRegionAssociation)
        .values(
            [
                {
                    "item_id": association.item_id,
                    "region_id": association.region_id,
                }
                for association in associations
            ]
        )
        .returning(ItemRegionAssociation)
    )

    # execute
    try:
        async with db.begin_nested():
            inserted_associations = (await db.execute(stmt)).unique().scalars().all()

    # If an IntegrityError is raised, it means either:
    # 1. Some regions do not exist
    # 2. Some items do not exist
    # 3. Unexpected error
    except IntegrityError as error:
        # raise RegionNotFoundError if a region does not exist (1.)
        await get_many_regions(
            db=db,
            region_ids={association.region_id for association in associations},
        )

        # raise ItemNotFoundError if an item does not exist (2.)
        await get_many_items(
            db=db,
            item_ids={association.item_id for association in associations},
        )

        # unexpected error (3.)
        raise error

    # Check the number of inserted associations matches the total number of
    # (item_id, region_id) tuples
    if len(inserted_associations) != len(associations):
        msg = (
            "The number of inserted item-region association s"
            f"({len(inserted_associations)}) does not match the number of given "
            f"associations ({len(associations)}). Unexpected reason"
        )
        raise RuntimeError(msg)


async def _insert_item_image_associations(
    db: AsyncSession,
    *,
    associations=list[InsertItemImageAssociation],
) -> None:
    """Insert item-image associations."""

    data = values(
        cast("ColumnClause[int]", ItemImageAssociation.item_id),
        column("order", Integer),
        cast("ColumnClause[str]", ItemImageAssociation.image_name),
        name="loan_request_data",
    ).data(
        [
            (association.item_id, association.order, association.image_name)
            for association in associations
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
            inserted_associations = (await db.execute(stmt)).unique().scalars().all()

    # If an IntegrityError is raised, it means either:
    # 1. Some images do not exist
    # 2. Some items do not exist
    # 3. Unexpected error
    except IntegrityError as error:
        # raises ItemImageNotFound if an image does not exist (1.)
        await get_many_images(
            db=db, image_names={association.image_name for association in associations}
        )
        # raises ItemNotFoundError if an item does not exist (2.)
        await get_many_items(
            db=db,
            item_ids={association.item_id for association in associations},
        )

        # unexpected error (3.)
        raise error

    # If the number of inserted associations does not match the number of given
    # associations, it means either:
    # 1. Some images are not owned by the same user that owns the item
    # 2. Unexpected Error
    if len(inserted_associations) != len(associations):
        # raise ItemImageNotOwnedError if an image is not owned
        await check_image_owners(
            db=db,
            image_owners=[
                CheckImageOwner(
                    image_name=association.image_name,
                    owner_id=association.owner_id,
                )
                for association in associations
            ],
        )

        msg = (
            "The number of inserted item-image associations "
            f"({len(inserted_associations)}) does not match the number "
            f"of given associations ({len(associations)}). Unexpected reason"
        )
        raise RuntimeError(msg)
