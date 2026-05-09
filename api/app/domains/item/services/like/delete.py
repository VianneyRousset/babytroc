from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.item.events import ItemUnliked
from app.domains.item.models import Item
from app.domains.item.models.like import ItemLike
from app.infrastructure.events import emit


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

    owner_id = (
        await db.execute(select(Item.owner_id).where(Item.id == item_id))
    ).scalar_one()

    await emit(
        db, ItemUnliked(item_id=item_id, user_id=user_id, item_owner_id=owner_id)
    )
