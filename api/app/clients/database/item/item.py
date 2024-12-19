from collections.abc import Collection
from typing import Any, Mapping, Optional

from sqlalchemy import Integer, func, select
from sqlalchemy.dialects.postgresql import INT4RANGE, Range
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.clients.database import dbutils
from app.clients.database.user import get_user
from app.errors.exception import ItemNotFoundError
from app.models.item import Item, ItemImage, Region
from app.models.user import User

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
    words: Optional[list[str]] = None,
    count: Optional[int] = 64,
    offset: Optional[int] = None,
    targeted_age_months: Optional[list[int]] = None,
    regions: Optional[list[int]] = None,
    owner_id: Optional[int] = None,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> list[Item]:
    """List items matchings criteria in the database.

    If the list of strings `words` is provided, those strings are used to filter the
    items based on their name and description via a fuzzy-search. This fuzzy-search also
    generates a score for each item.

    If `targeted_age_months` is provided, items with `targeted_age_months` range must
    overlap the given range to be returned.

    If `regions` is provided, items must be in one of those regions to
    be returned.

    If `owner_id` is provided, item must be owned by the user with this ID to be
    returned.

    If `count` is provided, the number of returned items is limited to `count`.

    If `offset` is provided, the `offset` items are skipped.

    The items are return sorted by descending ID (equivalent to creation date) and
    descending fuzzy-search score (which means the most relevant items are given first).
    """

    stmt = select(Item)

    stmt = dbutils.add_default_query_options(
        stmt=stmt,
        load_attributes=load_attributes,
        options=options,
    )

    # if words is provided, apply where filtering based on words matchings and sort
    # by distance based on word_similarity().
    if words:
        score = 0

        for word in words:
            score = score + Item.searchable_text.op("<->>", return_type=Integer)(
                func.normalize_text(word)
            )
            stmt = stmt.where(
                Item.searchable_text.op("%>", return_type=Integer)(
                    func.normalize_text(word)
                )
            )

        stmt = stmt.order_by(score)

    # if targeted_age_months is provided, apply where filtering based on range overlap
    if targeted_age_months is not None:
        if len(targeted_age_months) != 2:
            msg = (
                f"targeted_age_months must be of length 2, got: "
                f"{len(targeted_age_months)}."
            )
            raise ValueError(msg)

        targeted_age_months = Range(*targeted_age_months, bounds="[]")
        stmt = stmt.where(
            Item.targeted_age_months.op("&&", return_type=INT4RANGE)(
                targeted_age_months
            )
        )

    # if regions is provided, apply where filtering to select only the items
    # in the given region ids.
    if regions is not None:
        stmt = stmt.where(Item.regions.any(Region.id.in_(regions)))

    # if owner_id is provide, apply where filtering to select only the items
    # where owner_id is the ID of the owner.
    if owner_id is not None:
        stmt = stmt.where(Item.owner_id == owner_id)

    # if count is provided, limit number of results
    if count is not None:
        stmt = stmt.limit(count)

    # if offset is provided, offset the results
    if offset is not None:
        stmt = stmt.offset(offset)

    return (await db.scalars(stmt)).all()


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
        item = (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise ItemNotFoundError({"item_id": item_id}) from error

    return item


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

    if `owner_id` is provided, the item must be owned by the user with this ID.
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
