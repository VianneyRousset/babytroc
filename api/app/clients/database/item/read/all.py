from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item.query import ItemQueryFilter, ItemQueryPageCursor
from app.schemas.query import QueryPageOptions, QueryPageResult


def list_items(
    db: Session,
    *,
    query_filter: ItemQueryFilter | None = None,
    page_options: QueryPageOptions[ItemQueryPageCursor] | None = None,
) -> QueryPageResult[Item, ItemQueryPageCursor]:
    """List all items by decreasing id."""

    # default empty query filter
    query_filter = query_filter or ItemQueryFilter()

    # default empty query page options
    page_options = page_options or QueryPageOptions[ItemQueryPageCursor](
        cursor=ItemQueryPageCursor()
    )

    # selection
    stmt = select(Item)

    # apply filtering
    stmt = query_filter.apply(stmt)

    # apply ordering
    stmt = stmt.order_by(desc(Item.id))

    # apply pagination
    stmt = stmt.limit(page_options.limit)
    if page_options.cursor.item_id is not None:
        stmt = stmt.where(Item.id < page_options.cursor.item_id)

    items = list(db.execute(stmt).scalars().all())

    return QueryPageResult[Item, ItemQueryPageCursor](
        data=items,
        next_page_cursor=ItemQueryPageCursor(
            item_id=items[-1].id,
        ),
    )
