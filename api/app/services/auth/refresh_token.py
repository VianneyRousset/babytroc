import secrets
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, insert, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import AuthConfig
from app.errors.auth import (
    AuthAccountPasswordResetAuthorizationNotFoundError,
    AuthRefreshTokenNotFoundError,
    InvalidCredentialError,
)
from app.models.auth import AuthAccountPasswordResetAuthorization, AuthRefreshToken
from app.schemas.auth.query import AuthRefreshTokenReadQueryFilter
from app.schemas.auth.read import AuthRefreshTokenRead


async def create_refresh_token(
    db: AsyncSession,
    user_id: int,
    invalidated: bool = False,
) -> str:
    """Create a new refresh token for user with user_id."""

    stmt = (
        insert(AuthRefreshToken)
        .values(
            token=secrets.token_urlsafe(),
            user_id=user_id,
            invalidated=False,
        )
        .returning(AuthRefreshToken.token)
    )

    return (await db.execute(stmt)).unique().scalars().one()


async def verify_refresh_token(
    db: AsyncSession,
    token: str,
    config: AuthConfig,
) -> AuthRefreshTokenRead:
    """Check if given token exist, is not invalidated and is not expired.

    Raises InvalidCredentialError if token is not found, is invalidated or is expired.

    Returns the refresh token.
    """

    refresh_token = await get_refresh_token(
        db=db,
        token=token,
    )

    if refresh_token.invalidated:
        raise InvalidCredentialError()

    if is_refresh_token_expired(
        token_creation_date=refresh_token.creation_date,
        config=config,
    ):
        raise InvalidCredentialError()

    return AuthRefreshTokenRead.model_validate(refresh_token)


async def clean_user_refresh_tokens(
    db: AsyncSession,
    user_id: int,
    *,
    config: AuthConfig,
) -> None:
    """Remove all expired refresh tokens for the user with `user_id`."""

    tokens = await list_refresh_tokens(
        db=db,
        query_filter=AuthRefreshTokenReadQueryFilter(
            user_id=user_id,
        ),
    )

    for token in tokens:
        if is_refresh_token_expired(token.creation_date, config):
            await delete_refresh_token(db, token.token)


def is_refresh_token_expired(
    token_creation_date: datetime,
    config: AuthConfig,
) -> bool:
    """Returns True if `token_creation_date` is expired."""

    now = datetime.now(UTC)

    return now - token_creation_date > config.refresh_token_duration


async def get_refresh_token(
    db: AsyncSession,
    token: str,
    *,
    query_filter: AuthRefreshTokenReadQueryFilter | None = None,
) -> AuthRefreshToken:
    """Get auth refresh_token with `token` from database."""

    # default empty query filter
    query_filter = query_filter or AuthRefreshTokenReadQueryFilter()

    stmt = select(AuthRefreshToken).where(AuthRefreshToken.token == token)

    stmt = query_filter.filter_read(stmt)

    try:
        return (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"token": token}
        raise AuthRefreshTokenNotFoundError(key) from error


async def list_refresh_tokens(
    db: AsyncSession,
    *,
    query_filter: AuthRefreshTokenReadQueryFilter | None = None,
) -> list[AuthRefreshToken]:
    """List auth refresh_tokens matching criteria in the database."""

    # default empty query filter
    query_filter = query_filter or AuthRefreshTokenReadQueryFilter()

    # apply selection
    stmt = select(AuthRefreshToken)

    # apply filtering
    stmt = query_filter.filter_read(stmt)

    return list((await db.execute(stmt)).scalars().all())


async def list_account_password_reset_authorizations(
    db: AsyncSession,
) -> list[AuthAccountPasswordResetAuthorization]:
    """List account password reset authorizations from database."""

    stmt = select(AuthAccountPasswordResetAuthorization)

    return list((await db.execute(stmt)).scalars().all())


async def get_account_password_reset_authorization(
    db: AsyncSession,
    authorization_code: UUID,
) -> AuthAccountPasswordResetAuthorization:
    """Get account password reset authorization from database."""

    stmt = select(AuthAccountPasswordResetAuthorization).where(
        AuthAccountPasswordResetAuthorization.authorization_code == authorization_code
    )

    try:
        return (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise AuthAccountPasswordResetAuthorizationNotFoundError(
            {"authorization_code": authorization_code}
        ) from error


async def delete_refresh_token(
    db: AsyncSession,
    token: str,
) -> None:
    """Delete given token from database."""

    stmt = delete(AuthRefreshToken).where(AuthRefreshToken.token == token)

    # TODO check rowcount
    await db.execute(stmt)
