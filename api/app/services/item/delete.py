from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.item import ItemNotFoundError
from app.models.item import Item
from app.models.item.image import ItemImageAssociation
from app.models.item.region import ItemRegionAssociation
from app.schemas.item.query import ItemDeleteQueryFilter


async def delete_item(
    db: AsyncSession,
    item_id: int,
    *,
    query_filter: ItemDeleteQueryFilter | None = None,
) -> None:
    """Delete the item with ID `item_id`."""

    # default empty query filter
    query_filter = query_filter or ItemDeleteQueryFilter()

    stmt = query_filter.filter_delete(delete(Item).where(Item.id == item_id))

    res = await db.execute(stmt)

    if res.rowcount == 0:  # type: ignore[attr-defined]
        raise ItemNotFoundError({**query_filter.key, "id": item_id})


async def _delete_all_item_region_associations_of_item(
    db: AsyncSession,
    item_id: int,
) -> None:
    """Delete all item-regions associations with the given item_id."""

    stmt = delete(ItemRegionAssociation).where(ItemRegionAssociation.item_id == item_id)

    await db.execute(stmt)


async def _delete_all_item_image_associations_of_item(
    db: AsyncSession,
    item_id: int,
) -> None:
    """Delete all item-images associations with the given item_id."""

    stmt = delete(ItemImageAssociation).where(ItemImageAssociation.item_id == item_id)

    await db.execute(stmt)
