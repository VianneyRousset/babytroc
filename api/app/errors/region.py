from collections.abc import Mapping
from typing import Any

from .base import ApiError, NotFoundError


class RegionError(ApiError):
    """Exception related to a region."""

    pass


class RegionNotFoundError(RegionError, NotFoundError):
    """Exception raised when a region is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="region",
            key=key,
        )
