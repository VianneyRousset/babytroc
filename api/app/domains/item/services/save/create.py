from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.item.events import ItemSaved
from app.domains.item.models.save import ItemSave
from app.infrastructure.events import emit


async def add_item_to_user_saved_items(
    db: AsyncSession,
    *,
    item_id: int,
    user_id: int,
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

    await emit(db, ItemSaved(item_id=item_id, user_id=user_id))
