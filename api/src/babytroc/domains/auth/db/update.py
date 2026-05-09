from sqlalchemy.orm import Session

from babytroc.domains.auth.models import AuthRefreshToken


def invalidate_refresh_token(
    db: Session,
    token: AuthRefreshToken,
) -> None:
    """Delete given token from database."""

    token.invalidated = True
    db.refresh(token)
    db.flush()
