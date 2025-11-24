from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.user import UserNotFoundError
from app.models.user import User


async def delete_user(
    db: AsyncSession,
    user_id: int,
) -> None:
    """Delete user with `user_id`."""

    stmt = delete(User).where(User.id == user_id)

    res = await db.execute(stmt)

    if res.rowcount == 0:  # type: ignore[attr-defined]
        raise UserNotFoundError({"id": user_id})
