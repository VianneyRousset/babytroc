from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


def create_user(
    db: Session,
    *,
    email: str,
    name: str,
    password_hash: str,
    avatar_seed: Optional[str] = None,
) -> User:
    """Create and insert user into database."""

    user = User(
        email=email,
        name=name,
        password=password_hash,
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
