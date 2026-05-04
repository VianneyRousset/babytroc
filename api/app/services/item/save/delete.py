from typing import TYPE_CHECKING

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item.save import ItemSave

if TYPE_CHECKING:
    from app.clients.cache import Cache


async def remove_item_from_user_saved_items(
    db: AsyncSession,
    user_id: int,
    item_id: int,
    *,
    cache: "Cache | None" = None,
) -> None:
    """Remove item from user saved items."""

    stmt = delete(ItemSave).where(
        ItemSave.item_id == item_id,
        ItemSave.user_id == user_id,
    )

    await db.execute(stmt)

    if cache is not None:
        from app.services.item.cache import invalidate_item_saved

        await invalidate_item_saved(cache, saver_id=user_id)
