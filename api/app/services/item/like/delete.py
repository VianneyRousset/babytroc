from sqlalchemy.orm import Session

from app.clients import database


def remove_item_from_user_liked_items(
    db: Session,
    user_id: int,
    item_id: int,
):
    """Remove item from user liked items."""

    database.item.delete_item_like(
        db=db,
        user_id=user_id,
        item_id=item_id,
    )
