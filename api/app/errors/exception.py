from datetime import datetime
from http import HTTPStatus
from typing import Any, Mapping, Optional


class APIError(Exception):
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
        self.creation_date = creation_date

        super().__init__(message)


class NotFoundError(APIError):
    """Exception raised when something is not found."""

    def __init__(
        self,
        *,
        datatype: str,
        key: Mapping[str, Any],
        **kwargs,
    ):
        super().__init__(
            message=f"{datatype.capitalize()} with '{key!r}' not found.",
            **kwargs,
        )


class ItemError(APIError):
    """Exception related to an item."""

    pass


class ItemNotFoundError(NotFoundError, ItemError):
    """Exception raised when an item is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="item",
            key=key,
        )


class LoanRequestError(Exception):
    """Exception related to a loan request."""

    pass


class LoanRequestNotFoundError(NotFoundError, LoanRequestError):
    """Exception raised when a loan request is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="loan request",
            key=key,
        )


class LoanError(Exception):
    """Exception related to a loan."""

    pass


class LoanNotFoundError(NotFoundError, LoanError):
    """Exception raised when a loan is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="loan",
            key=key,
        )


class UserError(Exception):
    """Exception related to a user."""

    pass


class UserNotFoundError(NotFoundError, UserError):
    """Exception raised when a user is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="user",
            key=key,
        )
