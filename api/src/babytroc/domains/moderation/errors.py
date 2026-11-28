from collections.abc import Mapping
from typing import Any

from babytroc.shared.errors import ApiError, ConflictError, NotFoundError


class ModerationError(ApiError):
    """Exception related to the moderation."""


class ModeratorError(ApiError):
    """Exception related to moderators."""


class ModerationReportError(ApiError):
    """Exception related to moderation reports."""


class ModeratorAlreadyExistsError(ModeratorError, ConflictError):
    """Exception related to already existing moderators."""

    def __init__(self, *, user_id: int):

        message = f"Moderator #{user_id} already exists."
        super().__init__(message)


class ModeratorNotFoundError(ModeratorError, NotFoundError):
    """Exception related to non-existing moderators."""

    def __init__(self, key: Mapping[str, Any], **kwargs):

        super().__init__(
            datatype="moderator",
            key=key,
            **kwargs,
        )
