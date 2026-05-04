from typing import TYPE_CHECKING

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.models.item.like import ItemLike

if TYPE_CHECKING:
    from app.clients.cache import Cache


async def remove_item_from_user_liked_items(
    db: AsyncSession,
    user_id: int,
    item_id: int,
    *,
    cache: "Cache | None" = None,
) -> None:
    """Remove item from user liked items."""

    stmt = delete(ItemLike).where(
        ItemLike.item_id == item_id,
        ItemLike.user_id == user_id,
    )

    await db.execute(stmt)

    if cache is not None:
        from app.services.item.cache import invalidate_item_liked

        owner_id = (
            await db.execute(select(Item.owner_id).where(Item.id == item_id))
        ).scalar_one()
        await invalidate_item_liked(cache, liker_id=user_id, item_owner_id=owner_id)
