from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.clients.database.item import get_item
from app.clients.database.user import get_user
from app.errors.save import ItemSaveAlreadyExistsError
from app.models.item import Item


def create_item_save(
    db: Session,
    user_id: int,
    item_id: int,
) -> Item:
    """Create and insert an item save from `user_id` to item `item_id`."""

    user = get_user(
        db=db,
        user_id=user_id,
    )
    item = get_item(
        db=db,
        item_id=item_id,
    )

    item.saved_by.append(user)

    try:
        db.flush()

    except IntegrityError as error:
        raise ItemSaveAlreadyExistsError(
            user_id=user_id,
            item_id=item_id,
        ) from error

    return item
