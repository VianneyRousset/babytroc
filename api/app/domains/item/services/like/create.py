from typing import TYPE_CHECKING

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.item.models import Item
from app.domains.item.models.like import ItemLike

if TYPE_CHECKING:
    from app.clients.cache import Cache


async def add_item_to_user_liked_items(
    db: AsyncSession,
    *,
    item_id: int,
    user_id: int,
    cache: "Cache | None" = None,
) -> None:
    """Add the item with `item_id` to items liked by user with `user_id`."""

    # insertion
    stmt = insert(ItemLike).values(
        item_id=item_id,
        user_id=user_id,
    )

    # execute
    # TODO handle foreign key violation
    await db.execute(stmt)

    if cache is not None:
        from app.domains.item.services.cache import invalidate_item_liked

        owner_id = (
            await db.execute(select(Item.owner_id).where(Item.id == item_id))
        ).scalar_one()
        await invalidate_item_liked(cache, liker_id=user_id, item_owner_id=owner_id)
