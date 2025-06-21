from sqlalchemy import (
    BinaryExpression,
    BooleanClauseList,
    ColumnElement,
    Integer,
    func,
    select,
)
from sqlalchemy.orm import InstrumentedAttribute, Session

from app.models.item import Item
from app.schemas.item.query import ItemMatchingWordsQueryPageCursor, ItemQueryFilter
from app.schemas.query import QueryPageOptions, QueryPageResult


def list_items_matching_words(
    db: Session,
    words: list[str],
    *,
    query_filter: ItemQueryFilter | None = None,
    page_options: QueryPageOptions[ItemMatchingWordsQueryPageCursor] | None = None,
) -> QueryPageResult[Item, ItemMatchingWordsQueryPageCursor]:
    """List all items matching given words."""

    # default empty query filter
    query_filter = query_filter or ItemQueryFilter()

    # default empty query page options
    page_options = page_options or QueryPageOptions[ItemMatchingWordsQueryPageCursor](
        cursor=ItemMatchingWordsQueryPageCursor()
    )

    # selection
    words_match = _get_words_match(Item.searchable_text, words)
    stmt = select(Item, words_match)

    # apply filtering
    stmt = query_filter.apply(stmt)
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
    stmt = stmt.order_by(words_match)
    stmt = stmt.order_by(Item.id)

    # apply pagination
    stmt = stmt.limit(page_options.limit)
    if page_options.cursor.item_id is not None:
        stmt = stmt.where(words_match <= page_options.cursor.words_match)
        stmt = stmt.where(Item.id < page_options.cursor.item_id)

    items, words_matches = zip(*db.execute(stmt).scalars().all(), strict=True)

    # find next cursor
    return QueryPageResult[Item, ItemMatchingWordsQueryPageCursor](
        data=list(items),
        next_page_cursor=ItemMatchingWordsQueryPageCursor(
            words_match=words_matches[-1],
            item_id=items[-1].id,
        ),
    )


def normalized_word_distance(col: InstrumentedAttribute, word: str):
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
        return func.round(-normalized_word_distance(column, words[0]) * 1e5)

    distance = normalized_word_distance(column, words[0])

    for word in words[1:]:
        distance += normalized_word_distance(column, word)

    return func.round(-distance * 1e5)
