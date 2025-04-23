from sqlalchemy.orm import Session

from app.models.auth import AuthRefreshToken


def delete_refresh_token(
    db: Session,
    token: AuthRefreshToken,
) -> None:
    """Delete given token from database."""

    db.delete(token)
    db.flush()
