from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.item.events import ItemUnsaved
from app.domains.item.models.save import ItemSave
from app.infrastructure.events import emit


async def remove_item_from_user_saved_items(
    db: AsyncSession,
    user_id: int,
    item_id: int,
) -> None:
    """Remove item from user saved items."""

    stmt = delete(ItemSave).where(
        ItemSave.item_id == item_id,
        ItemSave.user_id == user_id,
    )

    await db.execute(stmt)

    await emit(db, ItemUnsaved(item_id=item_id, user_id=user_id))
