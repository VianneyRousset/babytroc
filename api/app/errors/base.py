from collections.abc import Mapping
from datetime import datetime
from http import HTTPStatus
from typing import Any, Optional


class ApiError(Exception):
    """Exception related to the API."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        creation_date: Optional[datetime] = None,
    ):
        if creation_date is None:
            creation_date = datetime.now()

        self.message = message
        self.status_code = status_code
        self.creation_date = creation_date.astimezone()

        super().__init__(message)


class NotFoundError(ApiError):
    """Cannot find a ressource."""

    def __init__(
        self,
        *,
        datatype: str,
        key: Mapping[str, Any],
        **kwargs,
    ):
        super().__init__(
            message=f"{datatype.capitalize()} with {key!r} not found.",
            status_code=HTTPStatus.NOT_FOUND,
            **kwargs,
        )


class ConflictError(ApiError):
    """Request conflict with the current state."""

    def __init__(
        self,
        message: str,
        **kwargs,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.CONFLICT,
            **kwargs,
        )


class BadRequestError(ApiError):
    """Client error in the request."""

    def __init__(
        self,
        message: str,
        **kwargs,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            **kwargs,
        )
