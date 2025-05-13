from sqlalchemy.orm import Session

from .read import get_item_like_by_user_item


def delete_item_like(
    db: Session,
    user_id: int,
    item_id: int,
) -> None:
    """Delete the item like from `user_id` to item `item_id`."""

    item_like = get_item_like_by_user_item(
        db=db,
        user_id=user_id,
        item_id=item_id,
    )

    db.delete(item_like)
    db.flush()
