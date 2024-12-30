from collections.abc import Mapping
from typing import Any

from .base import ApiError, NotFoundError


class ItemError(ApiError):
    """Exception related to an item."""

    pass


class ItemNotFoundError(ItemError, NotFoundError):
    """Exception raised when an item is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="item",
            key=key,
            **kwargs,
        )
