
from sqlalchemy.orm import Session

from app.models.auth import AuthRefreshToken


def create_refresh_token(
    db: Session,
    *,
    token: str,
    user_id: int,
    invalidated: bool | None = False,
) -> AuthRefreshToken:
    """Create and insert refresh_token into database."""

    db_token = AuthRefreshToken(
        token=token,
        user_id=user_id,
        invalidated=invalidated,
    )

    db.add(db_token)

    db.flush()
    db.refresh(db_token)

    return db_token
