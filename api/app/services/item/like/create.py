from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item.like import ItemLike


async def add_item_to_user_liked_items(
    db: AsyncSession,
    *,
    item_id: int,
    user_id: int,
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
