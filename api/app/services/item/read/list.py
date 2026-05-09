import json
from typing import TYPE_CHECKING, overload

from sqlalchemy import (
    BooleanClauseList,
    Integer,
    desc,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import undefer

from app.cache_keys import TTL_ITEMS_LIST, key_items_list
from app.models.item import Item
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import (
    ItemMatchingWordsQueryPageCursor,
    ItemQueryPageCursor,
    ItemReadQueryFilter,
)
from app.schemas.query import QueryPageOptions, QueryPageResult

from .selections import select_liked, select_owned, select_saved, select_words_match

if TYPE_CHECKING:
    from app.clients.cache import Cache


def _deserialize_list_result(
    raw: str,
    *,
    words: list[str] | None,
) -> (
    QueryPageResult[ItemPreviewRead, ItemQueryPageCursor]
    | QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor]
):
    """Deserialize a cached list_items result."""
    data = json.loads(raw)
    items = [ItemPreviewRead.model_validate(item) for item in data["items"]]
    npc = data["next_page_cursor"]

    if words is not None:
        return QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor](
            data=items,
            next_page_cursor=ItemMatchingWordsQueryPageCursor.model_validate(npc)
            if npc
            else None,
        )

    return QueryPageResult[ItemPreviewRead, ItemQueryPageCursor](
        data=items,
        next_page_cursor=ItemQueryPageCursor.model_validate(npc) if npc else None,
    )


def _build_cache_key(
    words: list[str] | None,
    query_filter: ItemReadQueryFilter,
    page_options: (
        QueryPageOptions[ItemQueryPageCursor]
        | QueryPageOptions[ItemMatchingWordsQueryPageCursor]
        | None
    ),
) -> str:
    """Build cache key for list_items."""
    return key_items_list(
        words=tuple(words) if words else None,
        query_filter=repr(query_filter),
        limit=page_options.limit if page_options else None,
    )


def _should_cache(
    cache: "Cache | None",
    client_id: int | None,
    page_options: (
        QueryPageOptions[ItemQueryPageCursor]
        | QueryPageOptions[ItemMatchingWordsQueryPageCursor]
        | None
    ),
) -> bool:
    """Return True if the request is cacheable (anonymous, first page)."""
    if cache is None or client_id is not None:
        return False
    if page_options is not None and page_options.cursor.item_id is not None:
        return False
    return True


def _serialize_list_result(
    items: list[ItemPreviewRead],
    next_page_cursor: ItemQueryPageCursor | ItemMatchingWordsQueryPageCursor | None,
) -> str:
    """Serialize a list_items result for caching."""
    return json.dumps({
        "items": [item.model_dump(mode="json") for item in items],
        "next_page_cursor": next_page_cursor.model_dump(mode="json")
        if next_page_cursor
        else None,
    })


@overload
async def list_items(
    db: AsyncSession,
    *,
    query_filter: ItemReadQueryFilter | None = None,
    page_options: QueryPageOptions[ItemQueryPageCursor] | None = None,
    client_id: int | None = None,
    cache: "Cache | None" = None,
) -> QueryPageResult[ItemPreviewRead, ItemQueryPageCursor]: ...


@overload
async def list_items(
    db: AsyncSession,
    words: list[str],
    *,
    query_filter: ItemReadQueryFilter | None = None,
    page_options: QueryPageOptions[ItemMatchingWordsQueryPageCursor] | None = None,
    client_id: int | None = None,
    cache: "Cache | None" = None,
) -> QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor]: ...


async def list_items(  # noqa: C901
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
    cache: "Cache | None" = None,
) -> (
    QueryPageResult[ItemPreviewRead, ItemQueryPageCursor]
    | QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor]
):
    """List items."""

    # default empty query filter
    query_filter = query_filter or ItemReadQueryFilter()

    # Only cache anonymous first-page requests
    use_cache = _should_cache(cache, client_id, page_options)
    cache_key = _build_cache_key(words, query_filter, page_options) if use_cache else ""

    cached = await cache.get(cache_key) if use_cache else None  # type: ignore[union-attr]
    if cached is not None:
        return _deserialize_list_result(cached, words=words)

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
        select_owned(client_id).label("owned_by_client"),
        select_liked(client_id).label("liked_by_client"),
        select_saved(client_id).label("saved_by_client"),
    ).select_from(Item)

    if words_match is not None:
        stmt = stmt.add_columns(words_match.label("words_match"))

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

        if cursor.words_match is not None and cursor.item_id is not None:
            # composite seek: everything strictly after (words_match, id) in
            # ORDER BY words_match DESC, id DESC
            stmt = stmt.where(
                BooleanClauseList.or_(
                    words_match < cursor.words_match,
                    BooleanClauseList.and_(
                        words_match == cursor.words_match,
                        Item.id < cursor.item_id,
                    ),
                )
            )
        elif cursor.words_match is not None:
            stmt = stmt.where(words_match <= cursor.words_match)
        elif cursor.item_id is not None:
            stmt = stmt.where(Item.id < cursor.item_id)

    elif cursor.item_id is not None:
        stmt = stmt.where(Item.id < cursor.item_id)

    stmt = stmt.options(undefer(Item.first_image_name))

    # execute
    res = await db.execute(stmt, {"client_id": client_id})
    rows = res.unique().all()

    items = [
        ItemPreviewRead.model_validate(
            {
                **{
                    k: getattr(row.Item, k)
                    for k in ItemPreviewRead.model_fields
                    if hasattr(row.Item, k)
                },
                "owned_by_client": row.owned_by_client,
                "liked_by_client": row.liked_by_client,
                "saved_by_client": row.saved_by_client,
            }
        )
        for row in rows
    ]

    if words_match is not None:
        next_cursor: ItemQueryPageCursor | ItemMatchingWordsQueryPageCursor | None = (
            ItemMatchingWordsQueryPageCursor(
                words_match=rows[-1].words_match,
                item_id=items[-1].id,
            )
            if rows
            else None
        )
        result = QueryPageResult[
            ItemPreviewRead, ItemMatchingWordsQueryPageCursor
        ](
            data=items,
            next_page_cursor=next_cursor,  # type: ignore[arg-type]
        )
    else:
        next_cursor = (
            ItemQueryPageCursor(item_id=items[-1].id) if items else None
        )
        result = QueryPageResult[ItemPreviewRead, ItemQueryPageCursor](  # type: ignore[assignment]
            data=items,
            next_page_cursor=next_cursor,  # type: ignore[arg-type]
        )

    if use_cache:
        await cache.set(  # type: ignore[union-attr]
            cache_key,  # type: ignore[possibly-undefined]
            _serialize_list_result(items, next_cursor),
            ttl=TTL_ITEMS_LIST,
        )

    return result
