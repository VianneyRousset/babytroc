from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.errors.item import ItemNotFoundError
from app.models.item import Item
from app.schemas.item.query import ItemQueryFilter


def delete_item(
    db: Session,
    item_id: int,
    *,
    query_filter: ItemQueryFilter | None = None,
) -> None:
    """Delete the item with ID `item_id`."""

    # default empty query filter
    query_filter = query_filter or ItemQueryFilter()

    stmt = delete(Item).where(Item.id == item_id)

    stmt = query_filter.apply(stmt)

    res = db.execute(stmt)

    if res.rowcount == 0:
        raise ItemNotFoundError({"id": item_id})
