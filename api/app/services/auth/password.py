from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.auth import IncorrectUsernameOrPasswordError
from app.models.user import User
from app.schemas.user.private import UserPrivateRead
from app.services.user.read import get_user_private


async def verify_user_password(
    db: AsyncSession,
    email: str,
    password: str,
) -> UserPrivateRead:
    """Verify username and password.

    Raises IncorrectUsernameOrPasswordError if no user with `email` exist or
    if the given password does not match the user password.

    Returns the user.
    """

    # get user by email
    stmt = select(User).where(User.email == email)

    try:
        res = await db.execute(stmt)
        user = res.unique().scalars().one()

    except NoResultFound as error:
        raise IncorrectUsernameOrPasswordError() from error

    # verify password
    if not user.password_hash.verify(password):
        raise IncorrectUsernameOrPasswordError()

    return await get_user_private(
        db=db,
        user_id=user.id,
    )
