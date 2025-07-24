from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.auth import IncorrectUsernameOrPasswordError
from app.models.user import User
from app.schemas.user.private import UserPrivateRead


def verify_user_password(
    db: Session,
    email: str,
    password: str,
) -> UserPrivateRead:
    """Verify username and password.

    Raises IncorrectUsernameOrPasswordError if no user with `email` exist or
    if the given password does not match the user password.

    Returns the user.
    """

    # get user by email
    try:
        user = (
            db.execute(select(User).where(User.email == email)).unique().scalars().one()
        )

    except NoResultFound as error:
        raise IncorrectUsernameOrPasswordError() from error

    # verify password
    if not user.password_hash.verify(password):
        raise IncorrectUsernameOrPasswordError()

    return UserPrivateRead.model_validate(user)
