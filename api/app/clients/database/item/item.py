from collections.abc import Collection
from typing import Any, Mapping, Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.clients.database import dbutils
from app.clients.database.user import get_user
from app.errors.exception import ItemNotFoundError
from app.models.item import Item, ItemImage
from app.models.user import User

from .region import get_region


async def create_item(
    db: Session,
    *,
    name: str,
    description: str,
    targeted_age: list[int],
    owner_id: int,
    images: list[str],
    regions: list[int],
    blocked: Optional[bool] = False,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> Item:
    """Create and insert item into database."""

    item = Item(
        name=name,
        description=description,
        targeted_age=targeted_age,
        blocked=blocked,
    )

    item.images.extend([ItemImage(id=image_id) for image_id in images])

    regions = [
        await get_region(
            db=db,
            region_id=region_id,
        )
        for region_id in regions
    ]
    item.regions.extend(regions)

    return await insert_item(
        db=db,
        item=item,
        owner_id=owner_id,
        load_attributes=load_attributes,
        options=options,
    )


async def insert_item(
    db: Session,
    item: Item,
    owner_id: int,
    *,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> Item:
    """Insert item into the database."""

    owner = await get_user(
        db=db,
        user_id=owner_id,
        load_attributes=[User.items],
    )

    owner.items.append(item)

    await db.flush()
    await db.refresh(item)

    return await get_item(
        db=db,
        item_id=item.id,
        load_attributes=load_attributes,
        options=options,
    )


async def list_items(
    db: Session,
    *,
    terms: Optional[list[str]] = None,
    targeted_age: Optional[list[int]] = None,
    regions: Optional[list[int]] = None,
    owner_id: Optional[int] = None,
    created_before_item_id: Optional[int] = None,
    count: Optional[int] = None,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> list[Item]:
    """List items matchings criteria in the database.

    The items are ordered by inversed ID which should reflect their creation date.

    If the list of strings `terms` is provided, those strings are used to filter the
    items based on their name and description. All the terms has to be present in the
    name or the description of the item to be returned.

    If `targeted_age` is provided, items with `targeted_age` range must overlap the
    given range to be returned.

    If `regions` is provided, the item must point to a least one of those regions to be
    returned.

    If `owner_id` is provided, the item must be owned by the user with this ID to be
    returned.

    If `created_before_item_id` is provided, only items created before that item id will
    be returned.

    If `count` is provided, the number of returned items is limited to `count`.
    """

    # TODO use quickwit or elasticsearch here

    stmt = select(Item).order_by(Item.id.desc())

    stmt = dbutils.add_default_query_options(
        stmt=stmt,
        load_attributes=load_attributes,
        options=options,
    )

    return (await db.scalars(stmt)).all()


async def get_item(
    db: Session,
    item_id: int,
    owner_id: Optional[int] = None,
    *,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> Item:
    """Get image with `image_id` from database.

    If `owner_id` is provided, the item must be owned by the user with this ID.
    """

    stmt = select(Item).where(Item.id == item_id)

    if owner_id is not None:
        stmt = stmt.where(Item.owner_id == owner_id)

    stmt = dbutils.add_default_query_options(
        stmt=stmt,
        load_attributes=load_attributes,
        options=options,
    )

    try:
        item = (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise ItemNotFoundError({"item_id": item_id}) from error

    return item


async def update_item(
    db: Session,
    item_id: int,
    *,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
    **attributes: Mapping[str, Any],
) -> Item:
    """Update the given `attributes` of the item with `item_id`."""

    item = await get_item(
        db=db,
        item_id=item_id,
        load_attributes=load_attributes,
        options=options,
    )

    for key, value in attributes.items():
        setattr(item, key, value)

    await db.flush()
    await db.reresh(item)

    return item


async def delete_item(
    db: Session,
    item_id: int,
    owner_id: Optional[int] = None,
) -> None:
    """Delete the item with `item_id` from database.

    If `owner_id` is provided, the item must be owned by the user with this ID.
    """

    item = await get_item(
        db=db,
        item_id=item_id,
        owner_id=owner_id,
    )

    await db.delete(item)
    await db.flush()
