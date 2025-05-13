from collections.abc import Mapping
from typing import Any

from app.errors.base import NotFoundError

from .base import ApiError


class ItemImageError(ApiError):
    """Exception related to an item image."""

    pass


class ItemImageNotFoundError(ItemImageError, NotFoundError):
    """Exception raised when an item image is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="image",
            key=key,
        )
