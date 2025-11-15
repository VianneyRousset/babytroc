from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.errors.user import UserNotFoundError
from app.models.user import User


def delete_user(
    db: Session,
    user_id: int,
) -> None:
    """Delete user with `user_id`."""

    stmt = delete(User).where(User.id == user_id)

    res = db.execute(stmt)

    if res.rowcount == 0:  # type: ignore[attr-defined]
        raise UserNotFoundError({"id": user_id})
