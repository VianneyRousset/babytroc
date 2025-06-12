from sqlalchemy.orm import Session

from app.models.auth import AuthAccountPasswordResetAuthorization, AuthRefreshToken


def delete_refresh_token(
    db: Session,
    token: AuthRefreshToken,
) -> None:
    """Delete given token from database."""

    db.delete(token)
    db.flush()


def delete_account_password_reset_authorization(
    db: Session,
    authorization: AuthAccountPasswordResetAuthorization,
) -> None:
    """Delete given account password reset authorization."""

    db.delete(authorization)
    db.flush()
