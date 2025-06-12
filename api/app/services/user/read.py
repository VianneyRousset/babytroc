from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.user.preview import UserPreviewRead
from app.schemas.user.private import UserPrivateRead
from app.schemas.user.query import UserQueryFilter
from app.schemas.user.read import UserRead


def get_user(
    db: Session,
    user_id: int,
) -> UserRead:
    """Get user with `user_id`."""

    # get user from database
    user = database.user.get_user(
        db=db,
        user_id=user_id,
    )

    return UserRead.model_validate(user)


def get_user_private(
    db: Session,
    user_id: int,
) -> UserPrivateRead:
    """Get user with `user_id`."""

    # get user from database
    user = database.user.get_user(
        db=db,
        user_id=user_id,
    )

    return UserPrivateRead.model_validate(user)


def list_users(
    db: Session,
) -> list[UserPreviewRead]:
    """List all users."""

    # get all users from database
    users = database.user.list_users(db=db)

    return [UserPreviewRead.model_validate(user) for user in users]


def get_user_exists(
    db: Session,
    query_filter: UserQueryFilter,
) -> bool:
    """Returns True if a user matching the `query_filter` exists."""

    return database.user.get_user_exists(db, query_filter)
