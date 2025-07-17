from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.models.item.like import ItemLike


def add_item_to_user_liked_items(
    db: Session,
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
    db.execute(stmt)
