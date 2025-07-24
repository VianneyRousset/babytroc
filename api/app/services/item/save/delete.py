from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.item.save import ItemSave


def remove_item_from_user_saved_items(
    db: Session,
    user_id: int,
    item_id: int,
) -> None:
    """Remove item from user saved items."""

    stmt = delete(ItemSave).where(
        ItemSave.item_id == item_id,
        ItemSave.user_id == user_id,
    )

    db.execute(stmt)
