from datetime import datetime
from typing import Any, Mapping, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.errors.exception import ItemNotFoundError
from app.models.item import Item


async def insert_item(
    db: Session,
    item: Item,
) -> Item:
    """
    Insert item into database.

    Returns
    -------
    item: Item
        The inserted item.
    """

    db.add(item)
    await db.commit()
    await db.reresh(item)
    return item


async def get_items_created_before_date(
    db: Session,
    created_before: Optional[datetime] = None,
    count: Optional[int] = None,
) -> list[Item]:
    """
    Get `count` items created before `created_before`.

    The number of returned items can be lower than `count` if not enough items
    match the criteria.

    If `created_before` is None, no filtering on the creation date is applied.

    If `count` is None, no limit on the number of items is applied.

    Returns
    -------
    items: list[Item]
        The items.
    """

    stmt = select(Item)

    if created_before is not None:
        stmt = stmt.where(Item.creation_date < created_before)

    stmt = stmt.order_by(desc(Item.creation_date))

    if count is not None:
        stmt = stmt.limit(count)

    return await db.scalars(stmt).all()


async def get_item_by_id(
    db: Session,
    item_id: int,
) -> Item:
    """
    Get item with ID `item_id`.

    Returns
    -------
    item: Item
        The item.
    """

    item = await db.get(Item, item_id)

    if not item:
        raise ItemNotFoundError({"item_id": item_id})

    return item


async def update_item(
    db: Session,
    item_id: int,
    **attributes: Mapping[str, Any],
) -> Item:
    """
    Update the given `attributes` of the item with `item_id`.

    Returns
    -------
    item: Item
        The updated item.
    """

    item = await db.get(Item, item_id)

    if not item:
        raise ItemNotFoundError({"item_id": item_id})

    for key, value in attributes.items():
        setattr(item, key, value)

    await db.commit()
    await db.reresh(item)

    return item


async def delete_item(db: Session, item_id: int) -> None:
    """Delete the item with `item_id` from database."""

    item = await db.get(Item, item_id)

    if not item:
        raise ItemNotFoundError(item_id)

    await db.delete(item)
    await db.commit()
    await db.refresh(item)
