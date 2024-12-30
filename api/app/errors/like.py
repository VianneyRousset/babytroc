from .base import ApiError, ConflictError


class ItemLikeError(ApiError):
    """Exception related to a item like."""

    pass


class ItemLikeAlreadyExistsError(ItemLikeError, ConflictError):
    """Exception related to an already existing item like."""

    def __init__(self, *, user_id: int, item_id: int):
        message = f"Item #{item_id} is already liked by user #{user_id}."
        super().__init__(message)


class ItemLikeNotExistsError(ItemLikeError, ConflictError):
    """Exception related to a non-existing item like."""

    def __init__(self, *, user_id: int, item_id: int):
        message = f"Item #{item_id} is not liked by user #{user_id}."
        super().__init__(message)
