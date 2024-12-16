from collections.abc import Collection
from typing import Any, Mapping, Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.exception import UserNotFoundError
from app.models.user import User

from . import dbutils


async def create_user(
    db: Session,
    *,
    email: str,
    name: str,
    password_hash: str,
    avatar_seed: Optional[str] = None,
) -> User:
    """Create and insert user into database."""

    user = User(
        email=email,
        name=name,
        password=password_hash,
        avatar_seed=avatar_seed,
    )

    return await insert_user(
        db=db,
        user=user,
    )


async def insert_user(
    db: Session,
    user: User,
) -> User:
    """Insert user into database."""

    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def list_users(
    db: Session,
    *,
    load_relationships: Optional[Collection[str]] = None,
) -> list[User]:
    stmt = select(User)

    stmt = dbutils.load_relationships(
        stmt=stmt,
        entity=User,
        load_relationships=load_relationships,
    )

    return (await db.scalars(stmt)).all()


async def get_user(
    db: Session,
    user_id: int,
    *,
    load_relationships: Optional[Collection[str]] = None,
) -> User:
    """Get user with `email` from database."""

    stmt = select(User).where(User.id == user_id)
    stmt = dbutils.load_relationships(
        stmt=stmt,
        entity=User,
        load_relationships=load_relationships,
    )

    try:
        user = (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"user_id": user_id}) from error

    return user


async def get_user_by_email(
    db: Session,
    email: str,
    *,
    load_relationships: Optional[Collection[str]] = None,
) -> User:
    """Get user with `email` from database."""

    stmt = select(User).where(User.email == email)
    stmt = dbutils.load_relationships(
        stmt=stmt,
        entity=User,
        load_relationships=load_relationships,
    )

    try:
        user = (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"email": email}) from error

    return user


async def update_user(
    db: Session,
    user_id: int,
    *,
    load_relationships: Optional[Collection[str]] = None,
    **attributes: Mapping[str, Any],
) -> User:
    """Update the given `attributes` of the user with `user_id`."""

    user = await get_user(
        db=db,
        user_id=user_id,
        load_relationships=load_relationships,
    )

    for key, value in attributes.items():
        setattr(user, key, value)

    await db.flush()
    await db.refresh(user)

    return user


async def delete_user(db: Session, user_id: int) -> None:
    """Delete the user with `user_id` from database."""

    user = await get_user(
        db=db,
        user_id=user_id,
    )

    await db.delete(user)
    await db.flush()
