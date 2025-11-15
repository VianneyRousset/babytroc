from sqlalchemy import update
from sqlalchemy.orm import Session

from app.errors.user import UserNotFoundError
from app.models.user import User


def add_stars_to_user(
    db: Session,
    user_id: int,
    count: int,
) -> None:
    """Add `count` stars to user with `user_id`."""

    stmt = (
        update(User)
        .values(stars_count=User.stars_count + count)
        .where(User.id == user_id)
    )

    # execute
    res = db.execute(stmt)

    if res.rowcount == 0:  # type: ignore[attr-defined]
        raise UserNotFoundError({"id": user_id})
