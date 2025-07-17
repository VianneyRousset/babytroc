from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.item import ItemNotFoundError
from app.models.item import Item
from app.schemas.item.query import ItemQueryFilter
from app.schemas.item.read import ItemRead
from app.schemas.item.update import ItemUpdate


def update_item(
    db: Session,
    *,
    item_id: int,
    item_update: ItemUpdate,
    query_filter: ItemQueryFilter | None = None,
) -> ItemRead:
    """Update item with `item_id`."""

    # default empty query filter
    query_filter = query_filter or ItemQueryFilter()

    stmt = update(Item).where(Item.id == item_id).values(**item_update.as_sql_values)

    stmt = query_filter.apply(stmt)

    stmt = stmt.returning(Item)

    result = db.execute(stmt)

    try:
        item = result.unique().scalars().one()

    except NoResultFound as error:
        key = {
            "item_id": item_id,
            **query_filter.key,
        }
        raise ItemNotFoundError(key) from error

    return ItemRead.model_validate(item)
