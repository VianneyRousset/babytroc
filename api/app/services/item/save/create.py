from sqlalchemy.orm import Session

from app.clients import database


def add_item_to_user_saved_items(
    db: Session,
    user_id: int,
    item_id: int,
) -> None:
    """Add the item with `item_id` to items saved by user with `user_id`."""

    database.save.create_item_save(
        db=db,
        user_id=user_id,
        item_id=item_id,
    )
