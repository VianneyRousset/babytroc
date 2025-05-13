from sqlalchemy.orm import Session

from .read import get_item_save_by_user_item


def delete_item_save(
    db: Session,
    user_id: int,
    item_id: int,
) -> None:
    """Delete the item save from `user_id` to item `item_id`."""

    item_save = get_item_save_by_user_item(
        db=db,
        user_id=user_id,
        item_id=item_id,
    )

    db.delete(item_save)
    db.flush()
