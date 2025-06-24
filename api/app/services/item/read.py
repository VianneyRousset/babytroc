from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.private import ItemPrivateRead
from app.schemas.item.query import (
    ItemMatchingWordsQueryPageCursor,
    ItemQueryFilter,
    ItemQueryPageCursor,
)
from app.schemas.item.read import ItemRead
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_item(
    db: Session,
    item_id: int,
    *,
    query_filter: ItemQueryFilter | None = None,
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
    query_filter: ItemQueryFilter | None = None,
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
    query_filter: ItemQueryFilter | None = None,
    page_options: QueryPageOptions[ItemQueryPageCursor] | None = None,
) -> QueryPageResult[ItemPreviewRead, ItemQueryPageCursor]:
    """List items."""

    # search items in database
    result = database.item.list_items(
        db=db,
        query_filter=query_filter,
        page_options=page_options,
    )

    return QueryPageResult[ItemPreviewRead, ItemQueryPageCursor](
        data=[ItemPreviewRead.model_validate(item) for item in result.data],
        next_page_cursor=result.next_page_cursor,
    )


def list_items_matching_words(
    db: Session,
    words: list[str],
    *,
    query_filter: ItemQueryFilter | None = None,
    page_options: QueryPageOptions[ItemMatchingWordsQueryPageCursor] | None = None,
) -> QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor]:
    """List items matching given words."""

    # search items in database
    # TODO discard words shorter than 3 characters ?
    result = database.item.list_items_matching_words(
        db=db,
        words=words,
        query_filter=query_filter,
        page_options=page_options,
    )

    return QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor](
        data=[ItemPreviewRead.model_validate(item) for item in result.data],
        next_page_cursor=result.next_page_cursor,
    )
