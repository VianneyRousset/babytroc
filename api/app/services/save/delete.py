from sqlalchemy.orm import Session

from app.clients import database


def remove_item_from_user_saved_items(
    db: Session,
    user_id: int,
    item_id: int,
):
    """Remove item from user saved items."""

    database.item.delete_item_save(
        db=db,
        user_id=user_id,
        item_id=item_id,
    )
