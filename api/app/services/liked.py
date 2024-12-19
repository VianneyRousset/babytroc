from typing import Optional

from sqlalchemy.orm import Session

from app import domain
from app.clients import database
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.read import ItemRead


async def add_item_to_user_liked_items(
    db: Session,
    user_id: int,
    item_id: int,
):
    """Add the item with `item_id` to items liked by user with `user_id`."""

    await database.item.create_item_like(
        db=db,
        user_id=user_id,
        item_id=item_id,
    )


async def remove_item_from_user_liked_items(
    db: Session,
    user_id: int,
    item_id: int,
):
    """Remove item from user liked items."""

    await database.item.delete_item_like(
        db=db,
        user_id=user_id,
        item_id=item_id,
    )
