from sqlalchemy import (
    BinaryExpression,
    BooleanClauseList,
    ColumnElement,
    Integer,
    and_,
    desc,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from app.models.item import Item, ItemLike, ItemSave
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import (
    ItemMatchingWordsQueryPageCursor,
    ItemReadQueryFilter,
)
from app.schemas.query import QueryPageOptions, QueryPageResult


async def list_items_matching_words(
    db: AsyncSession,
    words: list[str],
    *,
    query_filter: ItemReadQueryFilter | None = None,
    page_options: QueryPageOptions[ItemMatchingWordsQueryPageCursor] | None = None,
    client_id: int | None = None,
) -> QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor]:
    """List items matching given words."""

    # default empty query filter
    query_filter = query_filter or ItemReadQueryFilter()

    # default empty query page options
    page_options = page_options or QueryPageOptions[ItemMatchingWordsQueryPageCursor](
        cursor=ItemMatchingWordsQueryPageCursor()
    )

    # no client id
    if client_id is None:
        return await _list_items_matching_words_without_client_specific_fields(
            db=db,
            words=words,
            query_filter=query_filter,
            page_options=page_options,
        )

    # with client id
    return await _list_items_matching_words_with_client_specific_fields(
        db=db,
        words=words,
        query_filter=query_filter,
        page_options=page_options,
        client_id=client_id,
    )


async def _list_items_matching_words_without_client_specific_fields(
    db: AsyncSession,
    words: list[str],
    *,
    query_filter: ItemReadQueryFilter,
    page_options: QueryPageOptions[ItemMatchingWordsQueryPageCursor],
) -> QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor]:
    """List items without client specific fields."""

    # selection
    words_match = _get_words_match(Item.searchable_text, words)
    stmt = select(Item, words_match)

    # apply filtering
    stmt = query_filter.filter_read(stmt)

    # filter item without matching word
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

    # apply ordering
    stmt = stmt.order_by(desc(words_match))
    stmt = stmt.order_by(desc(Item.id))

    # apply pagination limit
    stmt = stmt.limit(page_options.limit)

    # apply pagination cursor
    if page_options.cursor.item_id is not None:
        stmt = stmt.where(words_match <= page_options.cursor.words_match)
        stmt = stmt.where(Item.id < page_options.cursor.item_id)

    # execute
    rows = (await db.execute(stmt)).unique().all()

    return QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor](
        data=[ItemPreviewRead.model_validate(item) for item, _ in rows],
        next_page_cursor=ItemMatchingWordsQueryPageCursor(
            words_match=rows[-1][1],
            item_id=rows[-1][0].id,
        )
        if rows
        else None,
    )


async def _list_items_matching_words_with_client_specific_fields(
    db: AsyncSession,
    words: list[str],
    *,
    query_filter: ItemReadQueryFilter,
    page_options: QueryPageOptions[ItemMatchingWordsQueryPageCursor],
    client_id: int,
) -> QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor]:
    """List items with client specific fields."""

    # selection
    words_match = _get_words_match(Item.searchable_text, words)
    stmt = (
        select(Item, words_match, ItemLike.id, ItemSave.id)
        .outerjoin(
            ItemLike, and_(ItemLike.item_id == Item.id, ItemLike.user_id == client_id)
        )
        .outerjoin(
            ItemSave, and_(ItemSave.item_id == Item.id, ItemSave.user_id == client_id)
        )
    )

    # apply filtering
    stmt = query_filter.filter_read(stmt)

    # filter item without matching word
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

    # apply ordering
    stmt = stmt.order_by(desc(words_match))
    stmt = stmt.order_by(desc(Item.id))

    # apply pagination limit
    stmt = stmt.limit(page_options.limit)

    # apply pagination cursor
    if page_options.cursor.item_id is not None:
        stmt = stmt.where(words_match <= page_options.cursor.words_match)
        stmt = stmt.where(Item.id < page_options.cursor.item_id)

    # execute
    rows = (await db.execute(stmt)).unique().all()

    return QueryPageResult[ItemPreviewRead, ItemMatchingWordsQueryPageCursor](
        data=[
            ItemPreviewRead.model_validate(
                {
                    **ItemPreviewRead.model_validate(item).model_dump(),
                    "owned": item.owner_id == client_id,
                    "liked": like_id is not None,
                    "saved": save_id is not None,
                }
            )
            for item, _, like_id, save_id in rows
        ],
        next_page_cursor=ItemMatchingWordsQueryPageCursor(
            words_match=rows[-1][1],
            item_id=rows[-1][0].id,
        )
        if rows
        else None,
    )


def _normalized_word_distance(col: InstrumentedAttribute, word: str):
    return col.op("<->>", return_type=Integer)(func.normalize_text(word))


def _get_words_match(
    column: InstrumentedAttribute,
    words: list[str],
) -> ColumnElement[int] | BinaryExpression[int]:
    """Expression of the words match distance between `column` and `words`.

    `words` are normalized and compared with `column` using `<->>` operator
    which is equivalent to the postgresql `word_similarity()` function.

    The returned distance is the sum of the distances of between `column`
    and each word in `words`.
    """

    if not words:
        msg = "Empty words"
        raise ValueError(msg)

    if len(words) == 1:
        return func.round(-_normalized_word_distance(column, words[0]) * 1e5)

    distance = _normalized_word_distance(column, words[0])

    for word in words[1:]:
        distance += _normalized_word_distance(column, word)

    return func.round(-distance * 1e5)
