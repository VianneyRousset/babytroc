from typing import TYPE_CHECKING

from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.errors import UserNotFoundError
from app.domains.user.models import User
from app.domains.user.schemas.private import UserPrivateRead
from app.domains.user.schemas.update import UserUpdate
from app.shared.hash import HashedStr

from .read import get_user_private

if TYPE_CHECKING:
    from app.infrastructure.cache_client import Cache


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
        from app.domains.user.services.cache import invalidate_user_updated

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
