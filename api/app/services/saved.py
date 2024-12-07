from typing import Optional

from sqlalchemy.orm import Session

from app import domain
from app.client import database
from app.schemas.item import ItemPreviewRead, ItemRead


async def add_item_to_user_saved_items(
    db: Session,
    user_id: int,
    item_id: int,
):
    """Add the item with `item_id` to items saved by user with `user_id`."""

    await database.item.insert_saved_item(
        db=db,
        user_id=user_id,
        item_id=item_id,
    )


async def list_items_saved_by_user(
    db: Session,
    user_id: int,
    saved_before_item_id: Optional[int] = None,
    count: Optional[int] = None,
) -> list[ItemPreviewRead]:
    """List items saved by user with `user_id`.

    If `saved_before_item_id` is provided, only items saved before that item id will
    be returned.

    If `count` is provided, the number of returned items is limited to `count`.
    """

    # search in db
    items = await database.item.list_items_saved_by_user(
        db=db,
        user_id=user_id,
        saved_before_item_id=saved_before_item_id,
        count=count,
    )

    return [ItemPreviewRead.model_validate(item) for item in items]


async def get_user_saved_item_by_id(
    db: Session,
    item_id: int,
    user_id: int,
    client_user_id: int,
) -> ItemRead:
    """Get item with `item_id`.

    The item has to be saved by user with `user_id`.
    """

    # get item from databse
    item = await database.item.get_item_by_id(
        db=db,
        item_id=item_id,
        saved_by_user_id=user_id,
    )

    # replace images by a list of image str ids (image urls)
    item.images = [img.id for img in item.images]

    # compute if the item is available
    item.available = domain.is_item_available(
        blocked=item.blocked,
        last_loan=item.loans,
    )

    # hide some infos if the client is not the owner of the item
    if item.owner.id != client_user_id:
        item.loans = None
        item.blocked = None

    return ItemRead.model_validate(item)


async def remove_item_from_user_like_items(
    db: Session,
    user_id: int,
    item_id: int,
):
    """Remove item from user like items."""

    await database.item.delete_item_like(
        db=db,
        user_id=user_id,
        item_id=item_id,
    )
