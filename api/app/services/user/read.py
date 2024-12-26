from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.user.preview import UserPreviewRead
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

    return UserRead.from_orm(user)


def list_users(
    db: Session,
) -> list[UserPreviewRead]:
    """List all users."""

    # get all users from database
    users = database.user.list_users(db=db)

    return [UserPreviewRead.from_orm(user) for user in users]
