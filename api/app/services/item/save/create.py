from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.item.read import ItemRead


def add_item_to_user_saved_items(
    db: Session,
    user_id: int,
    item_id: int,
) -> ItemRead:
    """Add the item with `item_id` to items saved by user with `user_id`."""

    item = database.save.create_item_save(
        db=db,
        user_id=user_id,
        item_id=item_id,
    )

    return ItemRead.from_orm(item)
