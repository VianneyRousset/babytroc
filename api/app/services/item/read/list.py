from typing import overload

from sqlalchemy import (
    BooleanClauseList,
    Integer,
    desc,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.schemas.item.base import MonthRange
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import (
    ItemMatchingWordsQueryPageCursor,
    ItemQueryPageCursor,
    ItemReadQueryFilter,
)
from app.schemas.query import QueryPageOptions, QueryPageResult

from .selections import (
    select_first_image,
    select_has_active_loan,
    select_liked,
    select_owned,
    select_saved,
    select_words_match,
)


@overload
async def list_items(
    db: AsyncSession,
    *,
    query_filter: ItemReadQueryFilter | None = None,
    page_options: QueryPageOptions[ItemQueryPageCursor] | None = None,
    client_id: int | None = None,
) -> QueryPageResult[ItemPreviewRead, ItemQueryPageCursor]: ...


@overload
async def list_items(
    db: AsyncSession,
    words: list[str],
    *,
    query_filter: ItemReadQueryFilter | None = None,
    page_options: QueryPageOptions[ItemMatchingWordsQueryPageCursor] | None = None,
    client_id: int | None = None,
) -> QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor]: ...


async def list_items(
    db: AsyncSession,
    words: list[str] | None = None,
    *,
    query_filter: ItemReadQueryFilter | None = None,
    page_options: (
        QueryPageOptions[ItemQueryPageCursor]
        | QueryPageOptions[ItemMatchingWordsQueryPageCursor]
        | None
    ) = None,
    client_id: int | None = None,
) -> (
    QueryPageResult[ItemPreviewRead, ItemQueryPageCursor]
    | QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor]
):
    """List items."""

    # default empty query filter
    query_filter = query_filter or ItemReadQueryFilter()

    # default empty query page options
    if page_options is None:
        page_options = (
            QueryPageOptions[ItemQueryPageCursor](cursor=ItemQueryPageCursor())
            if words is None
            else QueryPageOptions[ItemMatchingWordsQueryPageCursor](
                cursor=ItemMatchingWordsQueryPageCursor()
            )
        )

    words_match = (
        select_words_match(Item.searchable_text, words) if words is not None else None
    )

    stmt = select(
        Item,
        select_first_image().label("first_image"),
        select_has_active_loan().label("has_active_loan"),
        # select words match if `words` are given
        *([words_match.label("words_match")] if words_match is not None else []),
        # select client-specific fields if `client_id` is given
        *(
            [
                select_owned(client_id).label("owned"),
                select_liked(client_id).label("liked"),
                select_saved(client_id).label("saved"),
            ]
            if client_id is not None
            else []
        ),
    )

    # filter out items without words match
    if words is not None:
        stmt = stmt.where(
            BooleanClauseList.or_(
                *(
                    Item.searchable_text.op("%>", return_type=Integer)(
                        func.normalize_text(word)
                    )
                    for word in words
                )
            )
        )

    # apply filtering
    stmt = query_filter.filter_read(stmt)

    # apply ordering
    if words_match is not None:
        stmt = stmt.order_by(desc(words_match))
    stmt = stmt.order_by(desc(Item.id))

    # apply pagination limit
    stmt = stmt.limit(page_options.limit)

    # apply pagination cursor
    cursor = page_options.cursor
    if words_match is not None:
        if not isinstance(cursor, ItemMatchingWordsQueryPageCursor):
            msg = (
                f"Cursor is expected to be {ItemMatchingWordsQueryPageCursor} "
                "if `words` is not None."
            )
            raise TypeError(msg)

        if cursor.words_match is not None:
            stmt = stmt.where(words_match <= cursor.words_match)

    if cursor.item_id is not None:
        stmt = stmt.where(Item.id < cursor.item_id)

    # execute
    res = await db.execute(stmt)
    rows = res.unique().all()

    items = [
        ItemPreviewRead(
            id=row.Item.id,
            name=row.Item.name,
            targeted_age_months=MonthRange(row.Item.targeted_age_months),
            first_image=row.first_image,
            available=not (row.Item.blocked or row.has_active_loan),
            owner_id=row.Item.owner_id,
            owned=getattr(row, "owned", None),
            liked=getattr(row, "liked", None),
            saved=getattr(row, "saved", None),
        )
        for row in rows
    ]

    if words_match is not None:
        return QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor](
            data=items,
            next_page_cursor=ItemMatchingWordsQueryPageCursor(
                words_match=rows[-1].words_match,
                item_id=items[0].id,
            )
            if rows
            else None,
        )

    return QueryPageResult[ItemPreviewRead, ItemQueryPageCursor](
        data=items,
        next_page_cursor=ItemQueryPageCursor(
            item_id=items[-1].id,
        )
        if items
        else None,
    )
