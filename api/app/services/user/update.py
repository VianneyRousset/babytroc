from typing import TYPE_CHECKING

from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.user import UserNotFoundError
from app.models.user import User
from app.schemas.user.private import UserPrivateRead
from app.schemas.user.update import UserUpdate
from app.utils.hash import HashedStr

from .read import get_user_private

if TYPE_CHECKING:
    from app.clients.cache import Cache


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_update: UserUpdate,
    *,
    cache: "Cache | None" = None,
) -> UserPrivateRead:
    """Update user with `user_id`."""

    # update user fields
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(**user_update.model_dump(exclude_none=True))
        .returning(User.id)
    )

    try:
        (await db.execute(stmt)).one()
    except NoResultFound as error:
        raise UserNotFoundError({"id": user_id}) from error

    if cache is not None:
        from app.services.user.cache import invalidate_user_updated

        await invalidate_user_updated(cache, user_id=user_id)

    return await get_user_private(db=db, user_id=user_id)


async def update_user_password(
    db: AsyncSession,
    user_id: int,
    new_password: str | HashedStr,
) -> UserPrivateRead:
    """Update password of user with `user_id`."""

    new_password = HashedStr(new_password)

    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(password=new_password)
        .returning(User.id)
    )

    try:
        (await db.execute(stmt)).one()
    except NoResultFound as error:
        raise UserNotFoundError({"id": user_id}) from error

    return await get_user_private(db=db, user_id=user_id)


async def update_user_validation(
    db: AsyncSession,
    user_id: int,
    validated: bool,
) -> UserPrivateRead:
    """Update user validation state."""

    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(validated=validated)
        .returning(User.id)
    )

    try:
        (await db.execute(stmt)).one()
    except NoResultFound as error:
        raise UserNotFoundError({"id": user_id}) from error

    return await get_user_private(db=db, user_id=user_id)
