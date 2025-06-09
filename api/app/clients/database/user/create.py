from sqlalchemy.orm import Session

from app.models.user import User


def create_user(
    db: Session,
    *,
    email: str,
    name: str,
    password_hash: str,
    avatar_seed: str | None = None,
) -> User:
    """Create and insert user into database."""

    user = User(
        email=email,
        name=name,
        password_hash=password_hash,
        avatar_seed=avatar_seed,
    )

    return insert_user(
        db=db,
        user=user,
    )


def insert_user(
    db: Session,
    user: User,
) -> User:
    """Insert user into database."""

    db.add(user)
    db.flush()
    db.refresh(user)
    return user
