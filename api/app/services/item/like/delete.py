from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.item.like import ItemLike


def remove_item_from_user_liked_items(
    db: Session,
    user_id: int,
    item_id: int,
) -> None:
    """Remove item from user liked items."""

    stmt = delete(ItemLike).where(
        ItemLike.item_id == item_id,
        ItemLike.user_id == user_id,
    )

    db.execute(stmt)
