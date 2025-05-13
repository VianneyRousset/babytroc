from collections.abc import Mapping
from typing import Any

from .base import ApiError, NotFoundError


class ChatError(ApiError):
    """Exception related to a chat."""

    pass


class ChatNotFoundError(ChatError, NotFoundError):
    """Exception raised when a chat is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="chat",
            key=key,
        )


class ChatMessageError(ApiError):
    """Exception related to a chat message."""

    pass


class ChatMessageNotFoundError(ChatMessageError, NotFoundError):
    """Exception raised when a chat message is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="chat message",
            key=key,
        )
