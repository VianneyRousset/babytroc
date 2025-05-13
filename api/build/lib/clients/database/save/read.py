from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.save import ItemSaveNotFoundError
from app.models.item import ItemSave


def get_item_save_by_user_item(
    db: Session,
    *,
    user_id: int,
    item_id: int,
) -> ItemSave:
    """Get item save with `user_id` and `item_id`."""

    stmt = select(ItemSave)

    # filtering
    stmt = stmt.where(ItemSave.user_id == user_id).where(ItemSave.item_id == item_id)

    try:
        return db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        raise ItemSaveNotFoundError({"user_id": user_id, "item_id": item_id}) from error
