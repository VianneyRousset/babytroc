from typing import Optional

from sqlalchemy import BinaryExpression, Integer, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import InstrumentedAttribute, Session

from app.errors.item import ItemNotFoundError
from app.models.item import Item, ItemLike, ItemSave
from app.schemas.item.query import ItemQueryFilter
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_item(
    db: Session,
    item_id: int,
    *,
    query_filter: Optional[ItemQueryFilter] = None,
) -> Item:
    """Get item with `item_id` from database."""

    # default empty query filter
    query_filter = query_filter or ItemQueryFilter()

    stmt = select(Item).where(Item.id == item_id)

    stmt = query_filter.apply(stmt)

    try:
        return db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": item_id}
        raise ItemNotFoundError(key) from error


def list_items(
    db: Session,
    *,
    query_filter: Optional[ItemQueryFilter] = None,
    page_options: Optional[QueryPageOptions] = None,
) -> QueryPageResult[Item]:
    """List items matchings criteria in the database."""

    # default empty query filter
    query_filter = query_filter or ItemQueryFilter()

    # default empty query page options
    page_options = page_options or QueryPageOptions()

    # represents the word match distance
    if query_filter.words is None:
        words_match = None
    else:
        words_match = _get_words_match(Item.searchable_text, query_filter.words)

    like_id = ItemLike.id if query_filter.liked_by_user_id is not None else None
    save_id = ItemSave.id if query_filter.saved_by_user_id is not None else None

    stmt = select(Item, words_match, like_id, save_id)

    # apply filtering
    stmt = query_filter.apply(stmt)

    # apply pagination
    stmt = page_options.apply(
        stmt=stmt,
        columns={
            "item_id": Item.id,
            "words_match": words_match,
            "like_id": like_id,
            "save_id": save_id,
        },
    )

    rows = (db.execute(stmt)).all()

    if rows:
        items, words_matchs, like_ids, save_ids = zip(*rows)
    else:
        items, words_matchs, like_ids, save_ids = [], [], [], []

    return QueryPageResult[Item](
        data=items,
        order={
            "words_match": None if words_match is None else words_matchs,
            "like_id": None if like_id is None else like_ids,
            "save_id": None if save_id is None else save_ids,
            "item_id": [item.id for item in items],
        },
        desc=page_options.desc,
    )


def _get_words_match(
    column: InstrumentedAttribute, words: list[str]
) -> int | BinaryExpression:
    """Expression of the words match distance between `column` and `words`.

    `words` are normalized and compared with `column` using `<->>` operator
    which is equivalent to the postgresql `word_similarity()` function.

    The returned distance is the sum of the distances of between `column`
    and each word in `words`.
    """

    distance = 0

    for word in words:
        distance = distance - column.op("<->>", return_type=Integer)(
            func.normalize_text(word)
        )

    return func.cast(func.round(distance * 1e5), Integer)
