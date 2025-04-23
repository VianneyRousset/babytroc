import secrets
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.clients import database
from app.config import AuthConfig
from app.errors.auth import InvalidCredentialError
from app.schemas.auth.query import AuthRefreshTokenQueryFilter
from app.schemas.auth.read import AuthRefreshTokenRead


def create_refresh_token(
    db: Session,
    user_id: int,
) -> str:
    """Create a new refresh token for user with user_id."""

    token = database.auth.create_refresh_token(
        db=db,
        token=secrets.token_urlsafe(),
        user_id=user_id,
    )

    return token.token


def verify_refresh_token(
    db: Session,
    token: str,
    config: AuthConfig,
) -> AuthRefreshTokenRead:
    """Check if given token exist, is not invalidated and is not expired.

    Raises InvalidCredentialError if token is not found, is invalidated or is expired.

    Returns the refresh token.
    """

    refresh_token = database.auth.get_refresh_token(
        db=db,
        token=token,
    )

    if refresh_token.invalidated:
        raise InvalidCredentialError()

    print("refresh token not invalidated")

    if is_refresh_token_expired(
        token_creation_date=refresh_token.creation_date,
        config=config,
    ):
        print("refresh expired")
        raise InvalidCredentialError()

    print("refresh not expired")

    return AuthRefreshTokenRead.model_validate(refresh_token)


def clean_user_refresh_tokens(
    db: Session,
    user_id: int,
    *,
    config: AuthConfig,
) -> None:
    """Remove all expired refresh tokens for the user with `user_id`."""

    tokens = database.auth.list_refresh_tokens(
        db=db,
        query_filter=AuthRefreshTokenQueryFilter(
            user_id=user_id,
        ),
    )

    for token in tokens:
        if is_refresh_token_expired(token.creation_date, config):
            database.auth.delete_refresh_token(db, token)


def is_refresh_token_expired(
    token_creation_date: datetime,
    config: AuthConfig,
) -> bool:
    """Returns True if `token_creation_date` is expired."""

    now = datetime.now(UTC)

    return now - token_creation_date > config.refresh_token_duration
