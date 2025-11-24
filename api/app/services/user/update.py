from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.user import UserNotFoundError
from app.models.user import User
from app.schemas.user.private import UserPrivateRead
from app.schemas.user.update import UserUpdate
from app.utils.hash import HashedStr


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_update: UserUpdate,
) -> UserPrivateRead:
    """Update user with `user_id`."""

    # update user fields
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(**user_update.model_dump(exclude_none=True))
        .returning(User)
    )

    try:
        # execute
        user = (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"id": user_id}) from error

    return UserPrivateRead.model_validate(user)


async def update_user_password(
    db: AsyncSession,
    user_id: int,
    new_password: str | HashedStr,
) -> UserPrivateRead:
    """Update password of user with `user_id`."""

    new_password = HashedStr(new_password)

    # update user fields
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(password=new_password)
        .returning(User)
    )

    try:
        # execute
        user = (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"id": user_id}) from error

    return UserPrivateRead.model_validate(user)


async def update_user_validation(
    db: AsyncSession,
    user_id: int,
    validated: bool,
) -> UserPrivateRead:
    """Update user validation state."""

    stmt = (
        update(User.validated)
        .where(User.id == user_id)
        .values(validated=validated)
        .returning(User)
    )

    try:
        # execute
        user = (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"id": user_id}) from error

    return UserPrivateRead.model_validate(user)
