from typing import Optional

from sqlalchemy import BinaryExpression, Integer, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import InstrumentedAttribute, Session

from app.errors.exception import ItemNotFoundError
from app.models.item import Item, ItemLike, ItemSave
from app.schemas.item.query import (
    ItemQueryFilter,
    ItemQueryPageOptions,
    ItemQueryPageResult,
)


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
        return (db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        key = {"id": item_id, **query_filter.key()}
        raise ItemNotFoundError(key) from error


def list_items(
    db: Session,
    *,
    query_filter: Optional[ItemQueryFilter] = None,
    page_options: Optional[ItemQueryPageOptions] = None,
) -> ItemQueryPageResult[Item]:
    """List items matchings criteria in the database."""

    # default empty query filter
    query_filter = query_filter or ItemQueryFilter()

    # default empty query page options
    page_options = page_options or ItemQueryPageOptions()

    # represents the word match distance
    if query_filter.words is None:
        distance = None
    else:
        distance = _get_words_match_distance(Item.searchable_text, query_filter.words)

    like_id = ItemLike.id if query_filter.liked_by_user_id is not None else None
    save_id = ItemSave.id if query_filter.saved_by_user_id is not None else None

    stmt = select(Item, distance, like_id, save_id)

    stmt = query_filter.apply(stmt)
    stmt = page_options.apply(stmt, words_match_distance=distance)

    # set ordering
    if query_filter.words:
        stmt = stmt.order_by(distance)
    if query_filter.saved_by_user_id is not None:
        stmt = stmt.order_by(ItemSave.id.desc())
    if query_filter.liked_by_user_id is not None:
        stmt = stmt.order_by(ItemLike.id.desc())
    stmt = stmt.order_by(Item.id.desc())

    rows = (db.execute(stmt)).all()

    if rows:
        items, distances, like_ids, save_ids = zip(*rows)
    else:
        items, distances, like_ids, save_ids = [], [], [], []

    result = ItemQueryPageResult[Item].from_orm(
        items=items,
        words_match_distances=distances,
        like_ids=like_ids,
        save_ids=save_ids,
        query_filter=query_filter,
        page_options=page_options,
    )

    return result


def _get_words_match_distance(
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
        distance = distance + column.op("<->>", return_type=Integer)(
            func.normalize_text(word)
        )

    return distance
