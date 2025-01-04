from typing import Optional, cast

from sqlalchemy import (
    BinaryExpression,
    ColumnElement,
    Integer,
    func,
    select,
)
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

    active_selections = cast(
        dict[
            str,
            type[Item]
            | ColumnElement[int]
            | BinaryExpression[int]
            | InstrumentedAttribute,
        ],
        {"item": Item},
    )
    active_selections = {"item": Item}

    if query_filter.words:
        active_selections["words_match"] = _get_words_match(
            Item.searchable_text, query_filter.words
        )

    if query_filter.liked_by_user_id is not None:
        active_selections["like_id"] = ItemLike.id

    if query_filter.saved_by_user_id is not None:
        active_selections["save_id"] = ItemSave.id

    # apply selection
    stmt = select(*active_selections.values())

    # apply filtering
    stmt = query_filter.apply(stmt)

    # apply pagination
    stmt = page_options.apply(
        stmt=stmt,
        columns={
            "item_id": Item.id,
            "words_match": cast(
                ColumnElement[int] | BinaryExpression[int],
                active_selections.get("words_match"),
            ),
            "like_id": cast(InstrumentedAttribute, active_selections.get("like_id")),
            "save_id": cast(InstrumentedAttribute, active_selections.get("save_id")),
        },
    )

    rows = db.execute(stmt).all()

    result = {k: [row[n] for row in rows] for n, k in enumerate(active_selections)}

    order = {"item_id": [item.id for item in result["item"]]}

    for k in set(active_selections) - {"item"}:
        order[k] = result[k]

    return QueryPageResult[Item](
        data=result["item"],
        order=order,
        desc=page_options.desc,
    )


def normalized_word_distance(col: InstrumentedAttribute, word: str):
    return col.op("<->>", return_type=Integer)(func.normalize_text(word))


def _get_words_match(
    column: InstrumentedAttribute, words: list[str]
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

    distance = normalized_word_distance(column, words[0]) + normalized_word_distance(
        column, words[1]
    )

    for word in words:
        distance -= normalized_word_distance(column, word)

    return func.round(-distance * 1e5)
