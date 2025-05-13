from collections.abc import Mapping
from typing import Any

from .base import ApiError, NotFoundError


class UserError(ApiError):
    """Exception related to a user."""

    pass


class UserNotFoundError(UserError, NotFoundError):
    """Exception raised when a user is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="user",
            key=key,
        )
