from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from .base import ApiError, NotFoundError


class AuthError(ApiError):
    """Exception related to a authentification."""

    pass


class IncorrectUsernameOrPasswordError(AuthError):
    """Exception when an incorrect username or password is provided."""

    def __init__(self):
        super().__init__(
            message="Incorrect username or password",
            status_code=HTTPStatus.UNAUTHORIZED,
        )


class InvalidCredentialError(AuthError):
    """Credential is invalid."""

    def __init__(self):
        super().__init__(
            message="Could not validate credentials",
            status_code=HTTPStatus.UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthRefreshTokenNotFoundError(AuthError, NotFoundError):
    """Exception raised when a refresh_token is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="auth_refresh_token",
            key=key,
            **kwargs,
        )


class AuthAccountAlreadyValidatedError(AuthError):
    """Exception raised when an account is already validated but shouldn't be."""

    def __init__(self):
        super().__init__(
            message="Account already validated.",
            status_code=HTTPStatus.CONFLICT,
        )
