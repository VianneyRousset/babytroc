from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.user.create import UserCreate
from app.schemas.user.private import UserPrivateRead
from app.services.auth import hash_password


def create_user(
    db: Session,
    user_create: UserCreate,
) -> UserPrivateRead:
    """Create a user."""

    # insert new user in database
    user = database.user.create_user(
        db=db,
        email=user_create.email,
        name=user_create.name,
        password_hash=hash_password(user_create.password),
        avatar_seed=user_create.avatar_seed,
    )

    return UserPrivateRead.model_validate(user)
