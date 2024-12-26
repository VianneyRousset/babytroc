from typing import Any, Mapping

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
