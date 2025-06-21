from sqlalchemy import (
    select,
)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.item import ItemNotFoundError
from app.models.item import Item
from app.schemas.item.query import ItemQueryFilter


def get_item(
    db: Session,
    item_id: int,
    *,
    query_filter: ItemQueryFilter | None = None,
) -> Item:
    """Get item with `item_id` from database."""

    # default empty query filter
    query_filter = query_filter or ItemQueryFilter()

    stmt = select(Item).where(Item.id == item_id)

    stmt = query_filter.apply(stmt)

    try:
        return db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": item_id}
        raise ItemNotFoundError(key) from error
