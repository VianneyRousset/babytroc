from sqlalchemy.orm import Session

from app.clients import database
from app.config import AuthConfig
from app.schemas.auth.credentials import UserCredentials

from .access_token import create_access_token
from .password import verify_user_password
from .refresh_token import (
    clean_user_refresh_tokens,
    create_refresh_token,
    verify_refresh_token,
)


def login_user(
    db: Session,
    email: str,
    password: str,
    config: AuthConfig,
) -> UserCredentials:
    """Verifies password and create new credentials."""

    user = verify_user_password(
        db=db,
        email=email,
        password=password,
    )

    return create_user_credentials(
        db=db,
        user_id=user.id,
        validated=user.validated,
        config=config,
    )


def refresh_user_credentials(
    db: Session,
    refresh_token: str,
    config: AuthConfig,
) -> UserCredentials:
    """Verifies `refresh_token` and returns credentials with refreshed access token."""

    refresh_token_read = verify_refresh_token(
        db=db,
        token=refresh_token,
        config=config,
    )

    user = database.user.get_user(
        db=db,
        user_id=refresh_token_read.user_id,
    )

    return create_user_credentials(
        db=db,
        user_id=refresh_token_read.user_id,
        validated=user.validated,
        config=config,
        refresh_token=refresh_token,
    )


def create_user_credentials(
    db: Session,
    user_id: int,
    *,
    validated: bool,
    config: AuthConfig,
    refresh_token: str | None = None,
    access_token: str | None = None,
) -> UserCredentials:
    """Creates new credentials for user with `user_id`.

    If `refresh_token` is provided, the latter is used in the returned credentials
    and no refresh token is created.

    If `access_token` is provided, the latter is used in the returned credentials
    and no access token is created.
    """

    if refresh_token is None:
        refresh_token = create_refresh_token(
            db=db,
            user_id=user_id,
        )

    if access_token is None:
        access_token = create_access_token(
            user_id=user_id,
            config=config,
            validated=validated,
        )

    clean_user_refresh_tokens(
        db=db,
        user_id=user_id,
        config=config,
    )

    return UserCredentials(
        refresh_token=refresh_token,
        access_token=access_token,
        refresh_token_duration=config.refresh_token_duration,
        access_token_duration=config.access_token_duration,
    )
