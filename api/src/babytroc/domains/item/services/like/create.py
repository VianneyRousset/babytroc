from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.item.events import ItemLiked
from babytroc.domains.item.models import Item
from babytroc.domains.item.models.like import ItemLike
from babytroc.infrastructure.events import emit


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

    owner_id = (
        await db.execute(select(Item.owner_id).where(Item.id == item_id))
    ).scalar_one()

    await emit(db, ItemLiked(item_id=item_id, user_id=user_id, item_owner_id=owner_id))
