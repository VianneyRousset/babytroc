from typing import TYPE_CHECKING

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.moderation.errors import ModeratorNotFoundError
from babytroc.domains.user.models import User
from babytroc.domains.user.services import get_many_users_private

from .cache import invalidate_list_all_moderators

if TYPE_CHECKING:
    from babytroc.infrastructure.cache_client import Cache


async def delete_moderator(
    db: AsyncSession,
    user_id: int,
    *,
    cache: "Cache | None" = None,
) -> None:

    await delete_many_moderators(
        db=db,
        user_ids={user_id},
        cache=cache,
    )


async def delete_many_moderators(
    db: AsyncSession,
    user_ids: set[int],
    *,
    cache: "Cache | None" = None,
) -> None:

    stmt = (
        update(User).where(User.id.in_(user_ids)).values(moderator=True).returning(User)
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
                user_ids=user_ids,
            )

            # check if any user is already moderator (2.)
            for user in read_users:
                if not user.moderator:
                    raise ModeratorNotFoundError({"user_id": user.id})

            # unexpected error (3.)
            msg = (
                "The number of updated users does not match the number of given unique "
                " user ids. Unexpected reason."
            )
            raise RuntimeError(msg)

    if cache:
        await invalidate_list_all_moderators(cache)
