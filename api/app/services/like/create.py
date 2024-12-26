from sqlalchemy.orm import Session

from app.clients import database


def add_item_to_user_liked_items(
    db: Session,
    user_id: int,
    item_id: int,
) -> None:
    """Add the item with `item_id` to items liked by user with `user_id`."""

    database.like.create_item_like(
        db=db,
        user_id=user_id,
        item_id=item_id,
    )
