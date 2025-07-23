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


class AuthInvalidValidationCodeError(AuthError):
    """Exception raise when an invalid validation code is used."""

    def __init__(self):
        super().__init__(
            message="Invalid validation code",
            status_code=HTTPStatus.UNAUTHORIZED,
        )


class AuthAccountAlreadyValidatedError(AuthError):
    """Exception raised when an account is already validated but shouldn't be."""

    def __init__(self):
        super().__init__(
            message="Account already validated.",
            status_code=HTTPStatus.CONFLICT,
        )


class AuthUnauthorizedAccountPasswordResetError(AuthError):
    """Exception raised when an account password reset is unauthorized."""

    def __init__(self):
        super().__init__(
            message="Unauthorized account password reset.",
            status_code=HTTPStatus.UNAUTHORIZED,
        )


class AuthAccountPasswordResetAuthorizationNotFoundError(AuthError, NotFoundError):
    """Exception raised when a account password reset authorization is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="auth_account_password_reset_authorization",
            key=key,
            **kwargs,
        )
