from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.item.read import ItemRead


def remove_item_from_user_liked_items(
    db: Session,
    user_id: int,
    item_id: int,
) -> ItemRead:
    """Remove item from user liked items."""

    item = database.item.get_item(
        db=db,
        item_id=item_id,
    )

    database.like.delete_item_like(
        db=db,
        user_id=user_id,
        item_id=item_id,
    )

    return ItemRead.model_validate(item)
