from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.item import ItemNotFoundError
from app.models.item import Item
from app.schemas.item.query import ItemUpdateQueryFilter
from app.schemas.item.read import ItemRead
from app.schemas.item.update import ItemUpdate

from .create import (
    InsertItemImageAssociation,
    InsertItemRegionAssociation,
    _insert_item_image_associations,
    _insert_item_region_associations,
)
from .delete import (
    _delete_all_item_image_associations_of_item,
    _delete_all_item_region_associations_of_item,
)
from .read import get_item


async def update_item(
    db: AsyncSession,
    *,
    item_id: int,
    item_update: ItemUpdate,
    query_filter: ItemUpdateQueryFilter | None = None,
) -> ItemRead:
    """Update item with `item_id`.

    Raise ItemNotFoundError if no item with `item_id` matches the filters.
    """

    item = await _update_item_attributes(
        db=db,
        item_id=item_id,
        item_update=item_update,
        query_filter=query_filter,
    )

    if item_update.regions is not None:
        await _update_item_region_associations(
            db=db,
            item_id=item_id,
            region_ids=set(item_update.regions),
        )

    if item_update.images is not None:
        await _update_item_image_associations(
            db=db,
            item_id=item_id,
            owner_id=item.owner_id,
            image_names=item_update.images,
        )

    return await get_item(
        db=db,
        item_id=item_id,
    )


async def _update_item_attributes(
    db: AsyncSession,
    *,
    item_id: int,
    item_update: ItemUpdate,
    query_filter: ItemUpdateQueryFilter | None = None,
) -> Item:
    """Update the attributes of the item with `item_id`."""

    # default empty query filter
    query_filter = query_filter or ItemUpdateQueryFilter()

    stmt = query_filter.filter_update(
        update(Item)
        .where(Item.id == item_id)
        .values(item_update.as_sql_values(exclude={"images", "regions"}))
    ).returning(Item)

    # execute item update
    try:
        return (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise ItemNotFoundError({**query_filter.key, "id": item_id}) from error


async def _update_item_region_associations(
    db: AsyncSession,
    *,
    item_id: int,
    region_ids: set[int],
) -> None:
    # delete previous item-region associations
    await _delete_all_item_region_associations_of_item(
        db=db,
        item_id=item_id,
    )

    # re-insert new item-region associattions
    await _insert_item_region_associations(
        db=db,
        associations=InsertItemRegionAssociation.from_item_regions(
            item_id=item_id,
            region_ids=region_ids,
        ),
    )


async def _update_item_image_associations(
    db: AsyncSession,
    *,
    item_id: int,
    owner_id: int,
    image_names: list[str],
) -> None:
    # delete previous item-image associations
    await _delete_all_item_image_associations_of_item(
        db=db,
        item_id=item_id,
    )

    # re-insert new item-image associattions
    await _insert_item_image_associations(
        db=db,
        associations=InsertItemImageAssociation.from_item_images(
            item_id=item_id,
            owner_id=owner_id,
            image_names=image_names,
        ),
    )
