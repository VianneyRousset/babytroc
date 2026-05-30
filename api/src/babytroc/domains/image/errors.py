from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from babytroc.shared.errors import (
    ApiError,
    BadRequestError,
    ConflictError,
    NotFoundError,
)


class ItemImageError(ApiError):
    """Exception related to an item image."""


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


class ImageTooLargeError(ItemImageError):
    """Raised when an uploaded image exceeds the byte-size cap."""

    def __init__(self, actual: int, limit: int):
        super().__init__(
            f"Image too large: {actual} bytes (max {limit})",
            status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
        )


class ImagePixelLimitError(ItemImageError, BadRequestError):
    """Raised when an image's pixel count exceeds the decompression-bomb cap."""

    def __init__(self, max_pixels: int):
        super().__init__(f"Image exceeds max pixel count of {max_pixels}")


class InvalidImageError(ItemImageError, BadRequestError):
    """Raised when the uploaded bytes are not a recognisable image."""

    def __init__(self):
        super().__init__("Invalid or unreadable image file")
