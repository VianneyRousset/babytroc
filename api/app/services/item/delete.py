from typing import TYPE_CHECKING

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.item import ItemNotFoundError
from app.models.item import Item
from app.models.item.image import ItemImageAssociation
from app.models.item.region import ItemRegionAssociation
from app.schemas.item.query import ItemDeleteQueryFilter

if TYPE_CHECKING:
    from app.clients.cache import Cache


async def delete_item(
    db: AsyncSession,
    item_id: int,
    *,
    query_filter: ItemDeleteQueryFilter | None = None,
    cache: "Cache | None" = None,
) -> None:
    """Delete the item with ID `item_id`."""

    # default empty query filter
    query_filter = query_filter or ItemDeleteQueryFilter()

    # get owner_id before deleting (needed for cache invalidation)
    owner_id: int | None = None
    if cache is not None:
        owner_id = (
            await db.execute(select(Item.owner_id).where(Item.id == item_id))
        ).scalar()

    stmt = query_filter.filter_delete(delete(Item).where(Item.id == item_id))

    res = await db.execute(stmt)

    if res.rowcount == 0:  # type: ignore[attr-defined]
        raise ItemNotFoundError({**query_filter.key, "id": item_id})

    if cache is not None and owner_id is not None:
        from app.services.item.cache import invalidate_item_deleted

        await invalidate_item_deleted(cache, item_id=item_id, owner_id=owner_id)


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
