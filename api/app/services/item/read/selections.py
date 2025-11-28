from sqlalchemy import (
    BinaryExpression,
    ColumnElement,
    Exists,
    Integer,
    Select,
    and_,
    exists,
    func,
    select,
)
from sqlalchemy.orm import InstrumentedAttribute

from app.models.item import Item, ItemImageAssociation, ItemLike, ItemSave
from app.models.loan import Loan


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


def select_likes_count() -> Select:
    """Select the number of likes associated to the item."""

    return select(func.count(ItemLike.id)).where(
        ItemLike.item_id == Item.id,
    )


def select_first_image() -> Select:
    """Select the name of the first image associated to the item."""

    return (
        select(ItemImageAssociation.image_name)
        .where(
            ItemImageAssociation.item_id == Item.id,
        )
        .order_by(ItemImageAssociation.order)
        .limit(1)
    )


def select_has_active_loan() -> Exists:
    """Select true if the item has an active loan."""

    return exists(
        select(Loan.id).where(
            and_(
                Loan.item_id == Item.id,
                func.upper(Loan.during).is_not(None),
            ),
        )
    ).correlate(Item)


def select_owned(user_id: int) -> ColumnElement[bool]:
    """Select true if the item is owned by the given `user_id`."""

    return Item.owner_id == user_id


def select_liked(user_id: int) -> Exists:
    """Select true if the item is liked by the given `user_id`."""

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


def select_saved(user_id: int) -> Exists:
    """Select true if the item is saved by the given `user_id`."""

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
