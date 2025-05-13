from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.like import ItemLikeNotFoundError
from app.models.item import ItemLike


def get_item_like_by_user_item(
    db: Session,
    *,
    user_id: int,
    item_id: int,
) -> ItemLike:
    """Get item like with `user_id` and `item_id`."""

    stmt = select(ItemLike)

    # filtering
    stmt = stmt.where(ItemLike.user_id == user_id).where(ItemLike.item_id == item_id)

    try:
        return db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        raise ItemLikeNotFoundError({"user_id": user_id, "item_id": item_id}) from error
