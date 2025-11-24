from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item.like import ItemLike


async def remove_item_from_user_liked_items(
    db: AsyncSession,
    user_id: int,
    item_id: int,
) -> None:
    """Remove item from user liked items."""

    stmt = delete(ItemLike).where(
        ItemLike.item_id == item_id,
        ItemLike.user_id == user_id,
    )

    await db.execute(stmt)
