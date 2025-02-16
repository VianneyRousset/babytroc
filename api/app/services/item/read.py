from typing import Optional

from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.private import ItemPrivateRead
from app.schemas.item.query import ItemQueryFilter
from app.schemas.item.read import ItemRead
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_item(
    db: Session,
    item_id: int,
    *,
    query_filter: Optional[ItemQueryFilter] = None,
) -> ItemRead:
    """Get item by id."""

    # get item from databse
    item = database.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=query_filter,
    )

    return ItemRead.model_validate(item)


def get_private_item(
    db: Session,
    item_id: int,
    *,
    query_filter: Optional[ItemQueryFilter] = None,
) -> ItemPrivateRead:
    """Get item by id with private info"""

    # get item from databse
    item = database.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=query_filter,
    )

    return ItemPrivateRead.model_validate(item)


def list_items(
    db: Session,
    *,
    query_filter: Optional[ItemQueryFilter] = None,
    page_options: Optional[QueryPageOptions] = None,
) -> QueryPageResult[ItemPreviewRead]:
    """List items matchings criteria in the database."""

    # search items in database
    # TODO discard words shorter than 3 characters ?
    result = database.item.list_items(
        db=db,
        query_filter=query_filter,
        page_options=page_options,
    )

    result.data = [ItemPreviewRead.model_validate(item) for item in result.data]

    return QueryPageResult[ItemPreviewRead].model_validate(result)
