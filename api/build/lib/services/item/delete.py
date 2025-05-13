
from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.item.query import ItemQueryFilter


def delete_item(
    db: Session,
    item_id: int,
    *,
    query_filter: ItemQueryFilter | None = None,
):
    """Delete the item with ID `item_id`."""

    # find item in databas3
    item = database.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=query_filter,
    )

    # delete item
    database.item.delete_item(db=db, item=item)
