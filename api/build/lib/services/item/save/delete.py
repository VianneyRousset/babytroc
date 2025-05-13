from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.item.read import ItemRead


def remove_item_from_user_saved_items(
    db: Session,
    user_id: int,
    item_id: int,
) -> ItemRead:
    """Remove item from user saved items."""

    item = database.item.get_item(
        db=db,
        item_id=item_id,
    )

    database.save.delete_item_save(
        db=db,
        user_id=user_id,
        item_id=item.id,
    )

    return ItemRead.model_validate(item)
