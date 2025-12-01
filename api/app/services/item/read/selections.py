from sqlalchemy import (
    BinaryExpression,
    ColumnElement,
    Integer,
    and_,
    exists,
    func,
    literal,
    select,
)
from sqlalchemy.orm import InstrumentedAttribute

from app.models.item import Item, ItemLike, ItemSave


def _normalized_word_distance(col: InstrumentedAttribute, word: str):
    return col.op("<->>", return_type=Integer)(func.normalize_text(word))


def select_words_match(
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


def select_owned(user_id: int | None) -> ColumnElement[bool]:
    """Select true if the item is owned by the given `user_id`."""

    if user_id is None:
        return literal(None)

    return Item.owner_id == user_id


def select_liked(user_id: int | None) -> ColumnElement[bool]:
    """Select true if the item is liked by the given `user_id`."""

    if user_id is None:
        return literal(None)

    return exists(
        select(ItemLike.id)
        .where(
            and_(
                ItemLike.item_id == Item.id,
                ItemLike.user_id == user_id,
            ),
        )
        .correlate(Item)
    )


def select_saved(user_id: int | None) -> ColumnElement[bool]:
    """Select true if the item is saved by the given `user_id`."""

    if user_id is None:
        return literal(None)

    return exists(
        select(ItemSave.id)
        .where(
            and_(
                ItemSave.item_id == Item.id,
                ItemSave.user_id == user_id,
            ),
        )
        .correlate(Item)
    )
