from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.user import UserNotFoundError
from app.models.user import User


def get_user(
    db: Session,
    user_id: int,
) -> User:
    """Get user with `user_id` from database."""

    stmt = select(User).where(User.id == user_id)

    try:
        return (db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"id": user_id}) from error


def get_user_by_email(db: Session, email: str) -> User:
    """Get user with `email` from database."""

    stmt = select(User).where(User.email == email)

    try:
        return (db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"email": email}) from error


def list_users(
    db: Session,
) -> list[User]:
    """List users from database."""

    stmt = select(User)
    return list(db.scalars(stmt).all())
