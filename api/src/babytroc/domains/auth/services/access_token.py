from datetime import UTC, datetime

import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from babytroc.domains.auth.errors import InvalidCredentialError
from babytroc.domains.auth.schemas.data import UserAccessTokenData
from babytroc.infrastructure.config import AuthConfig


def create_access_token(
    *,
    user_id: int,
    validated: bool,
    config: AuthConfig,
    admin: bool = False,
    moderator: bool = False,
) -> str:
    """Create a new access token."""
    # issued at time
    iat = datetime.now(UTC)

    roles: list[str] = []

    if admin:
        roles.append("admin")

    if moderator:
        roles.append("moderator")

    return jwt.encode(
        payload={
            "iat": iat,
            "exp": iat + config.access_token_duration,
            "sub": str(user_id),
            "validated": validated,
            "realm_access": {
                "roles": roles,
            },
        },
        key=config.secret_key,
        algorithm=config.algorithm,
    )


def verify_access_token(
    token: str,
    *,
    config: AuthConfig,
) -> UserAccessTokenData:
    """Check that `token` is valid and not expired."""

    try:
        payload = jwt.decode(
            jwt=token,
            key=config.secret_key,
            algorithms=[config.algorithm],
        )

        return UserAccessTokenData(
            sub=payload["sub"],
            validated=payload["validated"],
            admin="admin" in payload.get("realm_access", {}).get("roles", []),
            moderator="moderator" in payload.get("realm_access", {}).get("roles", []),
        )

    except (InvalidTokenError, ValidationError) as error:
        raise InvalidCredentialError() from error
