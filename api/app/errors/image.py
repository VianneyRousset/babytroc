from collections.abc import Mapping
from typing import Any

from app.errors.base import ConflictError, NotFoundError

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


class ItemImageNotOwnedError(ItemImageError, ConflictError):
    """Exception raised when an item image is used but not owned by user."""

    def __init__(self, image_name_user_id: tuple[str, int] | set[tuple[str, int]]):
        super().__init__(
            "The following image(s) are not owned by the user (image_name, user_id): "
            f"{image_name_user_id}"
        )
