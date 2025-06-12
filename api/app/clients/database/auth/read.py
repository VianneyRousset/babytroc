from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.auth import (
    AuthAccountPasswordResetAuthorizationNotFoundError,
    AuthRefreshTokenNotFoundError,
)
from app.models.auth import AuthAccountPasswordResetAuthorization, AuthRefreshToken
from app.schemas.auth.query import AuthRefreshTokenQueryFilter


def get_refresh_token(
    db: Session,
    token: str,
    *,
    query_filter: AuthRefreshTokenQueryFilter | None = None,
) -> AuthRefreshToken:
    """Get auth refresh_token with `token` from database."""

    # default empty query filter
    query_filter = query_filter or AuthRefreshTokenQueryFilter()

    stmt = select(AuthRefreshToken).where(AuthRefreshToken.token == token)

    stmt = query_filter.apply(stmt)

    try:
        return db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"token": token}
        raise AuthRefreshTokenNotFoundError(key) from error


def list_refresh_tokens(
    db: Session,
    *,
    query_filter: AuthRefreshTokenQueryFilter | None = None,
) -> list[AuthRefreshToken]:
    """List auth refresh_tokens matching criteria in the database."""

    # default empty query filter
    query_filter = query_filter or AuthRefreshTokenQueryFilter()

    # apply selection
    stmt = select(AuthRefreshToken)

    # apply filtering
    stmt = query_filter.apply(stmt)

    return list(db.scalars(stmt).all())


def list_account_password_reset_authorizations(
    db: Session,
) -> list[AuthAccountPasswordResetAuthorization]:
    """List account password reset authorizations from database."""

    stmt = select(AuthAccountPasswordResetAuthorization)

    return list(db.scalars(stmt).all())


def get_account_password_reset_authorization(
    db: Session,
    authorization_code: UUID,
) -> AuthAccountPasswordResetAuthorization:
    """Get account password reset authorization from database."""

    stmt = select(AuthAccountPasswordResetAuthorization).where(
        AuthAccountPasswordResetAuthorization.authorization_code == authorization_code
    )

    try:
        return db.execute(stmt).scalars().one()

    except NoResultFound as error:
        raise AuthAccountPasswordResetAuthorizationNotFoundError(
            {"authorization_code": authorization_code}
        ) from error
