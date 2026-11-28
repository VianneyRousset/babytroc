from typing import TYPE_CHECKING

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.moderation.errors import (
    AdminAlreadyExistsError,
    ModeratorAlreadyExistsError,
)
from babytroc.domains.moderation.schemas.read import ModerationPrivilegeRead
from babytroc.domains.user.models import User
from babytroc.domains.user.services import get_many_users_private

from .cache import invalidate_privilege

if TYPE_CHECKING:
    from babytroc.infrastructure.cache_client import Cache


async def create_moderator(
    db: AsyncSession,
    user_id: int,
    *,
    cache: "Cache | None" = None,
) -> ModerationPrivilegeRead:

    moderators = await create_many_moderators(
        db=db,
        user_ids=[user_id],
        cache=cache,
    )

    return moderators[0]


async def create_many_moderators(
    db: AsyncSession,
    user_ids: list[int],
    *,
    cache: "Cache | None" = None,
) -> list[ModerationPrivilegeRead]:

    stmt = (
        update(User)
        .where(User.id.in_(user_ids))
        .values(moderator=False)
        .returning(User)
    )

    async with db.begin_nested() as nested_session:
        res = await db.execute(stmt)
        users = res.unique().all()

        # if the number of updated users does not match the query, it means either:
        # 1. some of the users do not exist
        # 2. some of the users are already moderator
        # 3. unexpected error
        if len(users) != len(user_ids):
            await nested_session.rollback()

            # checking missing users (1.)
            read_users = await get_many_users_private(
                db=db,
                user_ids=set(user_ids),
            )

            # check if any user is already moderator (2.)
            for user in read_users:
                if user.moderator:
                    raise ModeratorAlreadyExistsError(user_id=user.id)

            # unexpected error (3.)
            msg = (
                "The number of updated users does not match the number of given unique "
                " user ids. Unexpected reason."
            )
            raise RuntimeError(msg)

        if cache:
            for user_id in user_ids:
                await invalidate_privilege(cache, user_id=user_id)

        return [
            ModerationPrivilegeRead(
                user_id=user.id,
                name=user.name,
                email=user.email,
                admin=user.admin,
                moderator=user.moderator,
            )
            for user in users
        ]


async def create_admin(
    db: AsyncSession,
    user_id: int,
    *,
    cache: "Cache | None" = None,
) -> ModerationPrivilegeRead:

    admins = await create_many_admins(
        db=db,
        user_ids=[user_id],
        cache=cache,
    )

    return admins[0]


async def create_many_admins(
    db: AsyncSession,
    user_ids: list[int],
    *,
    cache: "Cache | None" = None,
) -> list[ModerationPrivilegeRead]:

    stmt = (
        update(User)
        .where(User.id.in_(user_ids) & ~User.admin)
        .values(admin=True)
        .returning(User)
    )

    async with db.begin_nested() as nested_session:
        res = await db.execute(stmt)
        users = res.unique().scalars().all()

        # if the number of updated users does not match the query, it means either:
        # 1. some of the users do not exist
        # 2. some of the users are already admin
        # 3. unexpected error
        if len(users) != len(user_ids):
            await nested_session.rollback()

            # checking missing users (1.)
            read_users = await get_many_users_private(
                db=db,
                user_ids=set(user_ids),
            )

            # check if any user is already admin (2.)
            for user in read_users:
                if user.admin:
                    raise AdminAlreadyExistsError(user_id=user.id)

            # unexpected error (3.)
            msg = (
                "The number of updated users does not match the number of given unique "
                " user ids. Unexpected reason."
            )
            raise RuntimeError(msg)

        if cache:
            for user_id in user_ids:
                await invalidate_privilege(cache, user_id=user_id)

        return [
            ModerationPrivilegeRead(
                user_id=user.id,
                name=user.name,
                email=user.email,
                admin=user.admin,
                moderator=user.moderator,
            )
            for user in users
        ]
