import logging
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.clients import database
from app.errors.auth import IncorrectUsernameOrPasswordError
from app.errors.base import NotFoundError
from app.schemas.user.read import UserRead

# silent passlib warning "module 'bcrypt' has no attribute '__about__'"
# https://github.com/pyca/bcrypt/issues/684
logging.getLogger("passlib").setLevel(logging.ERROR)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_user_account(
    db: Session,
    validation_code: UUID,
) -> None:
    """Mark user account with `validation_code` as validated."""

    user = database.user.get_user_by_validation_code(db, validation_code)

    database.user.mark_user_as_validated(db, user)


def verify_user_password(
    db: Session,
    email: str,
    password: str,
) -> UserRead:
    """Verify username and password.

    Raises IncorrectUsernameOrPasswordError if no user with `email` exist or
    if the given password does not match the user password.

    Returns the user.
    """

    # get user from database
    try:
        user = database.user.get_user_by_email(db, email)

    except NotFoundError as error:
        raise IncorrectUsernameOrPasswordError() from error

    # verify password
    if not verify_password_hash(
        plain_password=password,
        password_hash=user.password_hash,
    ):
        raise IncorrectUsernameOrPasswordError()

    return UserRead.model_validate(user)


def verify_password_hash(plain_password: str, password_hash: str) -> bool:
    """Returns True if `plan_password` matches `password hash`."""
    return pwd_context.verify(plain_password, password_hash)


def hash_password(password: str) -> str:
    """Returns a hashed version of `password`."""
    return pwd_context.hash(password)
