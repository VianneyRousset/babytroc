from typing import Optional

from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.item.private import ItemPrivateRead
from app.schemas.item.query import (
    ItemQueryFilter,
)
from app.schemas.item.update import ItemUpdate


def update_item(
    db: Session,
    *,
    item_id: int,
    item_update: ItemUpdate,
    query_filter: Optional[ItemQueryFilter] = None,
) -> ItemPrivateRead:
    """Update item with `item_id`."""

    # TODO check if images exists

    # get item
    item = database.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=query_filter,
    )

    # update item attributes
    item = database.item.update_item(
        db=db,
        item=item,
        attributes=item_update.dict(exclude_none=True),
    )

    return ItemPrivateRead.from_orm(item)
