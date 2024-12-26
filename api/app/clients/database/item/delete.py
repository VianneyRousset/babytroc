from sqlalchemy.orm import Session

from app.models.item import Item


def delete_item(
    db: Session,
    item: Item,
) -> None:
    """Delete the item with `item_id` from database."""

    db.delete(item)
    db.flush()
