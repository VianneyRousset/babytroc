import logging

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.auth import IncorrectUsernameOrPasswordError
from app.models.user import User
from app.schemas.user.private import UserPrivateRead

# silent passlib warning "module 'bcrypt' has no attribute '__about__'"
# https://github.com/pyca/bcrypt/issues/684
logging.getLogger("passlib").setLevel(logging.ERROR)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    if not verify_password_hash(
        plain_password=password,
        password_hash=user.password_hash,
    ):
        raise IncorrectUsernameOrPasswordError()

    return UserPrivateRead.model_validate(user)


def verify_password_hash(plain_password: str, password_hash: str) -> bool:
    """Returns True if `plan_password` matches `password hash`."""
    return pwd_context.verify(plain_password, password_hash)


def hash_password(password: str) -> str:
    """Returns a hashed version of `password`."""
    return pwd_context.hash(password)
