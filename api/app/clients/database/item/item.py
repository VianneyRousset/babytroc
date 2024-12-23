from collections.abc import Collection
from typing import Any, Mapping, Optional

from sqlalchemy import BinaryExpression, Integer, Select, func, select
from sqlalchemy.dialects.postgresql import INT4RANGE, Range
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import InstrumentedAttribute, Session

from app.clients.database import dbutils
from app.clients.database.user import get_user
from app.errors.exception import ItemNotFoundError
from app.models.item import Item, ItemImage, ItemLike, ItemSave, Region
from app.models.user import User
from app.schemas.item.query import (
    ItemQueryFilter,
    ItemQueryPageOptions,
    ItemQueryPageResult,
)

from .region import get_region


async def create_item(
    db: Session,
    *,
    name: str,
    description: str,
    targeted_age_months: list[int],
    owner_id: int,
    images: list[str],
    regions: list[int],
    blocked: Optional[bool] = False,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> Item:
    """Create and insert item into database."""

    item = Item(
        name=name,
        description=description,
        targeted_age_months=targeted_age_months,
        blocked=blocked,
    )

    item.images.extend([ItemImage(name=name) for name in images])

    regions = [
        await get_region(
            db=db,
            region_id=region_id,
        )
        for region_id in regions
    ]
    item.regions.extend(regions)

    return await insert_item(
        db=db,
        item=item,
        owner_id=owner_id,
        load_attributes=load_attributes,
        options=options,
    )


async def insert_item(
    db: Session,
    item: Item,
    owner_id: int,
    *,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> Item:
    """Insert item into the database."""

    owner = await get_user(
        db=db,
        user_id=owner_id,
        load_attributes=[User.items],
    )

    owner.items.append(item)

    await db.flush()
    await db.refresh(item)

    return await get_item(
        db=db,
        item_id=item.id,
        load_attributes=load_attributes,
        options=options,
    )


async def list_items(
    db: Session,
    *,
    query_filter: Optional[ItemQueryFilter] = None,
    page_options: Optional[ItemQueryPageOptions] = None,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> ItemQueryPageResult[Item]:
    """List items matchings criteria in the database.

    Order
    -----
    The items are return sorted by:
    - Increasing words match distance (the most relevant items are given first)
      if query_filter.words is provided.
    - Then, by descreasing `save_id` (the items saved the most recently
      are given first) if query_filter.saved_by_user_id is provided.
    - Then, by descreasing `like_id` (the items liked the most recently
      are given first) if query_filter.liked_by_user_id is provided.
    - Finally, by descreasing `item_id` (the items created most recently
      are given first.
    """

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or ItemQueryFilter()

    # if no page options are provided, use default page options
    page_options = page_options or ItemQueryPageOptions()

    # represents the word match distance
    if query_filter.words is None:
        distance = None
    else:
        distance = _get_words_match_distance(Item.searchable_text, query_filter.words)

    like_id = ItemLike.id if query_filter.liked_by_user_id is not None else None
    save_id = ItemSave.id if query_filter.saved_by_user_id is not None else None

    stmt = select(Item, distance, like_id, save_id)

    stmt = dbutils.add_default_query_options(
        stmt=stmt,
        load_attributes=load_attributes,
        options=options,
    )

    stmt = _apply_query_filter(stmt, query_filter, distance=distance)
    stmt = _apply_page_options(stmt, page_options, distance=distance)

    rows = (await db.execute(stmt)).all()

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


async def get_item(
    db: Session,
    item_id: int,
    owner_id: Optional[int] = None,
    *,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> Item:
    """Get image with `image_id` from database.

    If `owner_id` is provided, the item must be owned by the user with this ID.
    """

    stmt = select(Item).where(Item.id == item_id)

    if owner_id is not None:
        stmt = stmt.where(Item.owner_id == owner_id)

    stmt = dbutils.add_default_query_options(
        stmt=stmt,
        load_attributes=load_attributes,
        options=options,
    )

    try:
        return (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        key = {"item_id": item_id, "owner_id": owner_id}
        key = {k: v for k, v in key.items() if v is not None}
        raise ItemNotFoundError(key) from error


async def update_item(
    db: Session,
    item_id: int,
    *,
    owner_id: Optional[int] = None,
    attributes: Mapping[str, Any],
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> Item:
    """Update the given `attributes` of the item with `item_id`.

    If `owner_id` is provided, the item must be owned by the user with this ID.
    """

    # ensure modified attributes are loaded
    load_attributes = load_attributes or []
    load_attributes.extend(getattr(Item, attrname) for attrname in attributes)

    item = await get_item(
        db=db,
        item_id=item_id,
        owner_id=owner_id,
        load_attributes=load_attributes,
        options=options,
    )

    if "images" in attributes:
        attributes["images"] = [ItemImage(name=name) for name in attributes["images"]]

    # should raise 404 or something else ?
    if "regions" in attributes:
        attributes["regions"] = [
            await get_region(
                db=db,
                region_id=region_id,
            )
            for region_id in attributes["regions"]
        ]

    for key, value in attributes.items():
        setattr(item, key, value)

    await db.flush()
    await db.refresh(item)

    return item


async def delete_item(
    db: Session,
    item_id: int,
    owner_id: Optional[int] = None,
) -> None:
    """Delete the item with `item_id` from database.

    If `owner_id` is provided, the item must be owned by the user with this ID.
    """

    item = await get_item(
        db=db,
        item_id=item_id,
        owner_id=owner_id,
    )

    await db.delete(item)
    await db.flush()


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


def _apply_query_filter(
    stmt: Select,
    query_filter: ItemQueryFilter,
    *,
    distance: Integer,
) -> Select:
    """Add WHERE and ORDER BY operations according to `query_filter`."""

    # if words is provided, apply filtering based on words matchings
    if query_filter.words is not None:
        for word in query_filter.words:
            stmt = stmt.where(
                Item.searchable_text.op("%>", return_type=Integer)(
                    func.normalize_text(word)
                )
            )

        if query_filter.words:
            stmt = stmt.order_by(distance)

    # if targeted_age_months is provided, apply filtering based on range overlap
    if query_filter.targeted_age_months is not None:
        targeted_age_months = Range(*query_filter.targeted_age_months, bounds="[]")
        stmt = stmt.where(
            Item.targeted_age_months.op("&&", return_type=INT4RANGE)(
                targeted_age_months
            )
        )

    # if regions is provided, select items in the given regions
    if query_filter.regions is not None:
        stmt = stmt.where(Item.regions.any(Region.id.in_(query_filter.regions)))

    # if owner_id is provide, select items where owner_id is the given ID.
    if query_filter.owner_id is not None:
        stmt = stmt.where(Item.owner_id == query_filter.owner_id)

    # if saved_by_user_id is provided, select items saved by the given user ID.
    if query_filter.saved_by_user_id is not None:
        stmt = stmt.join(ItemSave).where(
            ItemSave.user_id == query_filter.saved_by_user_id
        )
        stmt = stmt.order_by(ItemSave.id.desc())

    # if liked_by_user_id is provided, select items liked by the given user ID.
    if query_filter.liked_by_user_id is not None:
        stmt = stmt.join(ItemLike).where(
            ItemLike.user_id == query_filter.liked_by_user_id
        )
        stmt = stmt.order_by(ItemLike.id.desc())

    # sort item by descending ID (equivalent to creation date ordering)
    stmt = stmt.order_by(Item.id.desc())

    return stmt


def _apply_page_options(
    stmt: Select,
    page_options: ItemQueryPageOptions,
    *,
    distance: Integer,
):
    """Add LIMIT and WHERE operations according to `page_options`."""

    # if limit is provided, limit number of results
    if page_options.limit is not None:
        stmt = stmt.limit(page_options.limit)

    # if item_id_lt is provided, select the item with ID less than the given value
    if page_options.item_id_lt is not None:
        stmt = stmt.where(Item.id < page_options.item_id_lt)

    # if words_match_distance_ge is provided, select items with words match distance
    # greater or equal to the given value
    if page_options.words_match_distance_ge is not None:
        stmt = stmt.where(distance >= page_options.words_match_distance_ge)

    # if like_id_le is provided, having a like with like_id less or equal
    # to the given value.
    if page_options.like_id_le is not None:
        stmt = stmt.where(ItemLike.id <= page_options.like_id_le)

    # if save_id_le is provided, having a save with save_id less or equal
    # to the given value.
    if page_options.save_id_le is not None:
        stmt = stmt.where(ItemSave.id <= page_options.save_id_le)

    return stmt
