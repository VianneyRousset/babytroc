from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.user import UserNotFoundError
from app.models.item import Item, ItemLike
from app.models.user import User
from app.schemas.user.preview import UserPreviewRead
from app.schemas.user.private import UserPrivateRead
from app.schemas.user.query import UserReadQueryFilter
from app.schemas.user.read import UserRead


async def get_user(
    db: AsyncSession,
    user_id: int,
) -> UserRead:
    """Get user with `user_id`."""

    users = await get_many_users(
        db=db,
        user_ids={user_id},
    )

    return users[0]


async def get_many_users(
    db: AsyncSession,
    user_ids: set[int],
) -> list[UserRead]:
    """Get all users with the given user ids.

    Raises UserNotFoundError if not all users matching criterias exist.
    """

    users = await get_many_users_private(
        db=db,
        user_ids=user_ids,
    )

    return [UserRead.model_validate(user) for user in users]


async def get_user_private(
    db: AsyncSession,
    user_id: int,
) -> UserPrivateRead:
    """Get user (including private info) with `user_id`."""

    users = await get_many_users_private(
        db=db,
        user_ids={user_id},
    )

    return users[0]


async def get_many_users_private(
    db: AsyncSession,
    user_ids: set[int],
) -> list[UserPrivateRead]:
    """Get all users (including private info) with the given user ids.

    Raises UserNotFoundError if not all users matching criterias exist.
    """

    stmt = (
        select(User, func.count(Item.id), func.count(ItemLike.id))
        .join(
            Item,
            onclause=Item.owner_id == User.id,
            isouter=True,
        )
        .join(
            ItemLike,
            onclause=ItemLike.item_id == Item.id,
            isouter=True,
        )
        .group_by(User.id)
    )

    print(stmt.compile(compile_kwargs={"literal_binds": True}), flush=True)

    res = await db.execute(stmt)
    rows = res.all()

    users = [
        UserPrivateRead(
            id=user.id,
            validated=user.validated,
            name=user.name,
            email=user.email,
            avatar_seed=user.avatar_seed,
            items_count=items_count,
            stars_count=user.stars_count,
            likes_count=likes_count,
        )
        for user, items_count, likes_count in rows
    ]

    missing_user_ids = user_ids - {user.id for user in users}
    if missing_user_ids:
        key = {"user_ids": missing_user_ids}
        raise UserNotFoundError(key)

    return users


async def get_user_by_email_private(
    db: AsyncSession,
    email: str,
) -> UserPrivateRead:
    """Get user with `email`."""

    stmt = select(User).where(User.email == email)

    try:
        # execute
        user = (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"email": email}) from error

    return UserPrivateRead.model_validate(user)


async def get_user_validation_code_by_email(
    db: AsyncSession,
    email: str,
) -> UUID:
    """Get validation code for user with `email`."""

    stmt = select(User.validation_code).where(User.email == email)

    try:
        # execute
        return (await db.execute(stmt)).unique().scalar_one()

    except NoResultFound as error:
        raise UserNotFoundError({"email": email}) from error


async def list_users(
    db: AsyncSession,
    *,
    query_filter: UserReadQueryFilter | None = None,
    limit: int | None = None,
) -> list[UserPreviewRead]:
    """List all users."""

    stmt = select(User)

    if query_filter is not None:
        stmt = query_filter.filter_read(stmt)

    if limit is not None:
        stmt = stmt.limit(limit)

    # execute
    users = (await db.execute(stmt)).unique().scalars().all()

    return [UserPreviewRead.model_validate(user) for user in users]
