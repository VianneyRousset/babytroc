from sqlalchemy.orm import Session

from app.models.user import User


def delete_user(
    db: Session,
    user: User,
) -> None:
    """Delete user from database."""

    db.delete(user)
    db.flush()
