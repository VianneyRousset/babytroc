from http import HTTPStatus
from typing import Literal

from fastapi.exceptions import HTTPException

from .base import AuthBase


class InvalidGrantTypeError(HTTPException):
    def __init__(self, grant_type: str):
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Invalid grant_type: {grant_type}",
        )


class MissingFieldError(HTTPException):
    def __init__(self, field: str):
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Missing field: {field}",
        )


class UnexpectedFieldError(HTTPException):
    def __init__(self, field: str):
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Unexpected field: {field}",
        )


class AuthPasswordForm(AuthBase):
    """Authentication form with username and password"""

    grant_type: Literal["password"]
    username: str
    password: str


class AuthRefreshTokenForm(AuthBase):
    """Authentication form with refresh token."""

    grant_type: Literal["refresh_token"]
    refresh_token: str
