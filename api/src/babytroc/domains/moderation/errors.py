from collections.abc import Mapping
from typing import Any

from babytroc.shared.errors import ApiError, ConflictError, NotFoundError


class ModerationError(ApiError):
    """Exception related to the moderation."""


class PrivilegeError(ApiError):
    """Exception related to priviledge."""


class ModerationReportError(ApiError):
    """Exception related to moderation reports."""


class AdminAlreadyExistsError(PrivilegeError, ConflictError):
    """Exception related to already existing admins."""

    def __init__(self, *, user_id: int):

        message = f"Admin #{user_id} already exists."
        super().__init__(message)


class AdminNotFoundError(PrivilegeError, NotFoundError):
    """Exception related to non-existing admins."""

    def __init__(self, key: Mapping[str, Any], **kwargs):

        super().__init__(
            datatype="admin",
            key=key,
            **kwargs,
        )


class ModeratorAlreadyExistsError(PrivilegeError, ConflictError):
    """Exception related to already existing moderators."""

    def __init__(self, *, user_id: int):

        message = f"Moderator #{user_id} already exists."
        super().__init__(message)


class ModeratorNotFoundError(PrivilegeError, NotFoundError):
    """Exception related to non-existing moderators."""

    def __init__(self, key: Mapping[str, Any], **kwargs):

        super().__init__(
            datatype="moderator",
            key=key,
            **kwargs,
        )
