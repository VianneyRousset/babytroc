from typing import TYPE_CHECKING

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.user.errors import UserNotFoundError
from babytroc.domains.user.models import User

if TYPE_CHECKING:
    from babytroc.infrastructure.cache_client import Cache


async def delete_user(
    db: AsyncSession,
    user_id: int,
    *,
    cache: "Cache | None" = None,
) -> None:
    """Delete user with `user_id`."""

    stmt = delete(User).where(User.id == user_id)

    res = await db.execute(stmt)

    if res.rowcount == 0:  # type: ignore[attr-defined]
        raise UserNotFoundError({"id": user_id})

    if cache is not None:
        from babytroc.domains.user.services.cache import invalidate_user_deleted

        await invalidate_user_deleted(cache, user_id=user_id)
