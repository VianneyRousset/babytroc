from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.user import UserNotFoundError
from app.models.user import User
from app.schemas.user.preview import UserPreviewRead
from app.schemas.user.private import UserPrivateRead
from app.schemas.user.query import UserQueryFilter
from app.schemas.user.read import UserRead


def get_user(
    db: Session,
    user_id: int,
) -> UserRead:
    """Get user with `user_id`."""

    return UserRead.model_validate(
        _get_user(
            db=db,
            user_id=user_id,
        )
    )


def get_user_private(
    db: Session,
    user_id: int,
) -> UserPrivateRead:
    """Get user with `user_id`."""

    return UserPrivateRead.model_validate(
        _get_user(
            db=db,
            user_id=user_id,
        )
    )


def get_user_by_email_private(
    db: Session,
    email: str,
) -> UserPrivateRead:
    """Get user with `email`."""

    stmt = select(User).where(User.email == email)

    try:
        # execute
        user = db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"email": email}) from error

    return UserPrivateRead.model_validate(user)


def get_user_validation_code_by_email(
    db: Session,
    email: str,
) -> UUID:
    """Get validation code for user with `email`."""

    stmt = select(User.validation_code).where(User.email == email)

    try:
        # execute
        return db.execute(stmt).unique().scalar_one()

    except NoResultFound as error:
        raise UserNotFoundError({"email": email}) from error


def list_users(
    db: Session,
    *,
    query_filter: UserQueryFilter | None,
    limit: int | None,
) -> list[UserPreviewRead]:
    """List all users."""

    stmt = select(User)

    if query_filter is not None:
        stmt = query_filter.apply(stmt)

    if limit is not None:
        stmt = stmt.limit(limit)

    # execute
    users = db.execute(stmt).unique().scalars().all()

    return [UserPreviewRead.model_validate(user) for user in users]


def _get_user(
    db: Session,
    user_id: int,
) -> User:
    """Get db user model with `user_id`."""

    stmt = select(User).where(User.id == user_id)

    try:
        # execute
        return db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        raise UserNotFoundError({"id": user_id}) from error
