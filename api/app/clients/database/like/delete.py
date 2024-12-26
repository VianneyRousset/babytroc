from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import Item, ItemLike
from app.models.user import User


def delete_item_like(
    db: Session,
    user_id: int,
    item_id: int,
) -> None:
    """Delete the item like from `user_id` to item `item_id`."""

    item_like = (
        select(ItemLike).where(User.id == user_id).where(Item.id == item_id).scalar()
    )

    db.delete(item_like)
    db.flush()
