from typing import TYPE_CHECKING

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.item.models.save import ItemSave

if TYPE_CHECKING:
    from app.infrastructure.cache_client import Cache


async def add_item_to_user_saved_items(
    db: AsyncSession,
    *,
    item_id: int,
    user_id: int,
    cache: "Cache | None" = None,
) -> None:
    """Add the item with `item_id` to items saved by user with `user_id`."""

    # insertion
    stmt = insert(ItemSave).values(
        item_id=item_id,
        user_id=user_id,
    )

    # execute
    # TODO handle foreign key violation
    await db.execute(stmt)

    if cache is not None:
        from app.domains.item.services.cache import invalidate_item_saved

        await invalidate_item_saved(cache, saver_id=user_id)
