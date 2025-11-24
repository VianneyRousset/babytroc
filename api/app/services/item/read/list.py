from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item, ItemLike, ItemSave
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import (
    ItemQueryPageCursor,
    ItemReadQueryFilter,
)
from app.schemas.query import QueryPageOptions, QueryPageResult


async def list_items(
    db: AsyncSession,
    *,
    query_filter: ItemReadQueryFilter | None = None,
    page_options: QueryPageOptions[ItemQueryPageCursor] | None = None,
    client_id: int | None = None,
) -> QueryPageResult[ItemPreviewRead, ItemQueryPageCursor]:
    """List items."""

    # default empty query filter
    query_filter = query_filter or ItemReadQueryFilter()

    # default empty query page options
    page_options = page_options or QueryPageOptions[ItemQueryPageCursor](
        cursor=ItemQueryPageCursor()
    )

    # no client id
    if client_id is None:
        return await _list_items_without_client_specific_fields(
            db=db,
            query_filter=query_filter,
            page_options=page_options,
        )

    # with client id
    return await _list_items_with_client_specific_fields(
        db=db,
        query_filter=query_filter,
        page_options=page_options,
        client_id=client_id,
    )


async def _list_items_without_client_specific_fields(
    db: AsyncSession,
    *,
    query_filter: ItemReadQueryFilter,
    page_options: QueryPageOptions[ItemQueryPageCursor],
) -> QueryPageResult[ItemPreviewRead, ItemQueryPageCursor]:
    """List items without client specific fields."""

    stmt = select(Item)

    # apply filtering
    stmt = query_filter.filter_read(stmt)

    # apply ordering
    stmt = stmt.order_by(desc(Item.id))

    # apply pagination limit
    stmt = stmt.limit(page_options.limit)

    # apply pagination cursor
    if page_options.cursor.item_id is not None:
        stmt = stmt.where(Item.id < page_options.cursor.item_id)

    # execute
    items = (await db.execute(stmt)).unique().scalars().all()

    return QueryPageResult[ItemPreviewRead, ItemQueryPageCursor](
        data=[ItemPreviewRead.model_validate(item) for item in items],
        next_page_cursor=ItemQueryPageCursor(
            item_id=items[-1].id,
        )
        if items
        else None,
    )


async def _list_items_with_client_specific_fields(
    db: AsyncSession,
    *,
    query_filter: ItemReadQueryFilter,
    page_options: QueryPageOptions[ItemQueryPageCursor],
    client_id: int,
) -> QueryPageResult[ItemPreviewRead, ItemQueryPageCursor]:
    """List items with client specific fields."""

    stmt = (
        select(Item, ItemLike.id, ItemSave.id)
        .outerjoin(
            ItemLike, and_(ItemLike.item_id == Item.id, ItemLike.user_id == client_id)
        )
        .outerjoin(
            ItemSave, and_(ItemSave.item_id == Item.id, ItemSave.user_id == client_id)
        )
    )

    # apply filtering
    stmt = query_filter.filter_read(stmt)

    # apply ordering
    stmt = stmt.order_by(desc(Item.id))

    # apply pagination limit
    stmt = stmt.limit(page_options.limit)

    # apply pagination cursor
    if page_options.cursor.item_id is not None:
        stmt = stmt.where(Item.id < page_options.cursor.item_id)

    # execute
    rows = (await db.execute(stmt)).unique().all()

    return QueryPageResult[ItemPreviewRead, ItemQueryPageCursor](
        data=[
            ItemPreviewRead.model_validate(
                {
                    **ItemPreviewRead.model_validate(item).model_dump(),
                    "owned": item.owner_id == client_id,
                    "liked": like_id is not None,
                    "saved": save_id is not None,
                }
            )
            for item, like_id, save_id in rows
        ],
        next_page_cursor=ItemQueryPageCursor(
            item_id=rows[-1][0].id,
        )
        if rows
        else None,
    )
