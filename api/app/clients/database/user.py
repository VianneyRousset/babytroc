from typing import Any, Mapping

from sqlalchemy.orm import Session

from app.errors.exception import UserNotFoundError
from app.models.user import User


async def insert_user(
    db: Session,
    user: User,
) -> User:
    """
    Insert user into database.

    Returns
    -------
    user: User
        The inserted user.
    """

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_email(
    session: Session,
    email: str,
) -> User:
    """
    Get user with `email` from database.

    Returns
    -------
    user: User
        The user.
    """

    user = session.query(User).filter(User.email == email).one()

    if not user:
        return UserNotFoundError({"email": email})

    return user


async def update_user(
    db: Session,
    user_id: int,
    **attributes: Mapping[str, Any],
) -> User:
    """
    Update the given `attributes` of the user with `user_id`.

    Returns
    -------
    user: User
        The updated user.
    """

    user = await db.get(User, user_id)

    if not user:
        return UserNotFoundError({"user_id": user_id})

    for key, value in attributes.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return user


async def delete_user(db: Session, user_id: int) -> None:
    """Delete the user with `user_id` from database."""

    user = await db.get(User, user_id)

    if not user:
        return UserNotFoundError({"user_id": user_id})

    await db.delete(user)
    await db.commit()
