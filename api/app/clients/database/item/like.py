from collections.abc import Collection
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.clients.database.user import get_user
from .item import get_item
from app.errors.exception import ItemLikeAlreadyExistsError
from app.models.item import ItemLike, Item
from app.models.user import User


async def create_item_like(
    db: Session,
    user_id: int,
    item_id: int,
) -> None:
    """Create and insert an item like from `user_id` to item `item_id`."""

    user = await get_user(
        db=db,
        user_id=user_id,
    )
    item = await get_item(
        db=db,
        item_id=item_id,
        load_attributes=[Item.liked_by],
    )

    item.liked_by.append(user)

    try:
        await db.flush()

    except IntegrityError as error:
        raise ItemLikeAlreadyExistsError(
            user_id=user_id,
            item_id=item_id,
        ) from error


async def delete_item_like(
    db: Session,
    user_id: int,
    item_id: int,
) -> None:
    """Delete the item like from `user_id` to item `item_id`."""

    item_like = (
        select(ItemLike).where(User.id == user_id).where(Item.id == item_id).scalar()
    )

    await db.delete(item_like)
    await db.flush()
