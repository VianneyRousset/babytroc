from collections.abc import Mapping
from typing import Any

from .base import ApiError, ConflictError, NotFoundError


class ItemLikeError(ApiError):
    """Exception related to a item like."""

    pass


class ItemLikeAlreadyExistsError(ItemLikeError, ConflictError):
    """Exception related to an already existing item like."""

    def __init__(self, *, user_id: int, item_id: int):
        message = f"Item #{item_id} is already liked by user #{user_id}."
        super().__init__(message)


class ItemLikeNotFoundError(ItemLikeError, NotFoundError):
    """Exception related to a non-existing item like."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="item like",
            key=key,
            **kwargs,
        )
