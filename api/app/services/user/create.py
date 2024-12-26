from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.user.create import UserCreate
from app.schemas.user.read import UserRead


def create_user(
    db: Session,
    user_create: UserCreate,
) -> UserRead:
    """Create a user."""

    # TODO password hash

    # insert new user in database
    user = database.user.create_user(
        db=db,
        email=user_create.email,
        name=user_create.name,
        password_hash=user_create.password,
        avatar_seed=user_create.avatar_seed,
    )

    return UserRead.from_orm(user)
