from typing import cast

from sqlalchemy import ColumnClause, Integer, column, update, values
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.user.read import get_many_users


async def add_stars_to_user(
    db: AsyncSession,
    user_id: int,
    count: int,
) -> None:
    """Add `count` stars to user with `user_id`."""

    await add_many_stars_to_users(
        db=db,
        user_ids_stars_counts={user_id: count},
    )


async def add_many_stars_to_users(
    db: AsyncSession,
    user_ids_stars_counts: dict[int, int],
):
    data = values(
        cast("ColumnClause[int]", User.id),
        column("added_stars_count", Integer),
        name="user_add_star_data",
    ).data(list(user_ids_stars_counts.items()))

    stmt = (
        update(User)
        .values(
            stars_count=User.stars_count + data.c.added_stars_count,
        )
        .where(User.id == data.c.user_id)
    )

    # execute
    res = await db.execute(stmt)

    # If not all users has been updated, it means either:
    # 1. Some users do not exist
    # 2. Unexpected error
    if res.rowcount == len(user_ids_stars_counts):  # type: ignore[attr-defined]
        # raises UserNotFoundError if a user does not exist (1.)
        await get_many_users(
            db=db,
            user_ids=set(user_ids_stars_counts.keys()),
        )

        # unexpected error
        msg = (
            "The number of updated users does not match the number of "
            "(user_id, stars_count) tuples. Unexpected reason."
        )
        raise RuntimeError(msg)
