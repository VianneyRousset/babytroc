from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import Item, ItemSave
from app.models.user import User


def delete_item_save(
    db: Session,
    user_id: int,
    item_id: int,
) -> None:
    """Delete the item save from `user_id` to item `item_id`."""

    item_save = (
        select(ItemSave).where(User.id == user_id).where(Item.id == item_id).scalar()
    )

    db.delete(item_save)
    db.flush()
