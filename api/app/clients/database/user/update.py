from collections.abc import Mapping
from typing import Any

from sqlalchemy.orm import Session

from app.models.user import User


def update_user(
    db: Session,
    user: User,
    attributes: Mapping[str, Any],
) -> User:
    """Update the given `attributes` of `user`."""

    for key, value in attributes.items():
        setattr(user, key, value)

    db.flush()
    db.refresh(user)

    return user


def mark_user_as_validated(
    db: Session,
    user: User,
) -> User:
    """Set user `validated` flag to True."""

    user.validated = True
    db.flush()
    db.refresh(user)

    return user


def add_stars_to_user(
    db: Session,
    user: User,
    count: int,
) -> User:
    """Add `count` stars to `user`'s `stars_count`."""

    user.stars_count += count

    db.flush()
    db.refresh(user)

    return user
