from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.user import UserNotFoundError
from app.models.user import User
from app.schemas.user.private import UserPrivateRead
from app.schemas.user.update import UserUpdate
from app.services.auth import hash_password


def update_user(
    db: Session,
    user_id: int,
    user_update: UserUpdate,
) -> UserPrivateRead:
    """Update user with `user_id`."""

    # update user fields
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(**user_update.model_dump(exclude_none=True))
        .returning(User)
    )

    try:
        # execute
        user = db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"id": user_id}) from error

    return UserPrivateRead.model_validate(user)


def update_user_password(
    db: Session,
    user_id: int,
    new_password: str,
) -> UserPrivateRead:
    """Update password of user with `user_id`."""

    # update user fields
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(password=hash_password(new_password))
        .returning(User)
    )

    try:
        # execute
        user = db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"id": user_id}) from error

    return UserPrivateRead.model_validate(user)


def update_user_validation(
    db: Session,
    user_id: int,
    validated: bool,
) -> UserPrivateRead:
    """Update user validation state."""

    stmt = (
        update(User.validated)
        .where(User.id == user_id)
        .values(validated=validated)
        .returning(User)
    )

    try:
        # execute
        user = db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"id": user_id}) from error

    return UserPrivateRead.model_validate(user)
