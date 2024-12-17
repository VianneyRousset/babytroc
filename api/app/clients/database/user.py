from collections.abc import Collection
from typing import Any, Mapping, Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.exception import UserNotFoundError
from app.models.user import User

from app.clients.database import dbutils


async def create_user(
    db: Session,
    *,
    email: str,
    name: str,
    password_hash: str,
    avatar_seed: Optional[str] = None,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
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
        load_attributes=load_attributes,
        options=options,
    )


async def insert_user(
    db: Session,
    user: User,
    *,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> User:
    """Insert user into database."""

    db.add(user)
    await db.flush()
    await db.refresh(user)
    return await get_user(
        db=db,
        user_id=user.id,
        load_attributes=load_attributes,
        options=options,
    )


async def list_users(
    db: Session,
    *,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> list[User]:
    stmt = select(User)

    stmt = dbutils.add_default_query_options(
        stmt=stmt,
        load_attributes=load_attributes,
        options=options,
    )

    return (await db.scalars(stmt)).all()


async def get_user(
    db: Session,
    user_id: int,
    *,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> User:
    """Get user with `email` from database."""

    stmt = select(User).where(User.id == user_id)
    stmt = dbutils.add_default_query_options(
        stmt=stmt,
        load_attributes=load_attributes,
        options=options,
    )

    for option in options or []:
        stmt = stmt.options(option)

    try:
        user = (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"user_id": user_id}) from error

    return user


async def get_user_by_email(
    db: Session,
    email: str,
    *,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> User:
    """Get user with `email` from database."""

    stmt = select(User).where(User.email == email)
    stmt = dbutils.add_default_query_options(
        stmt=stmt,
        load_attributes=load_attributes,
        options=options,
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
    attributes: Mapping[str, Any],
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> User:
    """Update the given `attributes` of the user with `user_id`."""

    user = await get_user(
        db=db,
        user_id=user_id,
        load_attributes=load_attributes,
        options=options,
    )

    for key, value in attributes.items():
        setattr(user, key, value)

    await db.flush()
    await db.refresh(user)

    return user


async def add_stars_to_user(
    db: Session,
    user_id: int,
    *,
    added_stars_count: int,
):
    """Add `new_stars_count` stars to user with ID `user_id`."""

    user = await get_user(
        db=db,
        user_id=user_id,
        load_attributes=[User.stars_count],
    )

    user.stars_count = user.stars_count + added_stars_count

    await db.flush()
    await db.refresh(user)

    return user


async def delete_user(
    db: Session,
    user_id: int,
) -> None:
    """Delete the user with `user_id` from database."""

    user = await get_user(
        db=db,
        user_id=user_id,
    )

    await db.delete(user)
    await db.flush()
