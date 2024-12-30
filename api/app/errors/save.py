from .base import ApiError, ConflictError


class ItemSaveError(ApiError):
    """Exception related to a item save."""

    pass


class ItemSaveAlreadyExistsError(ItemSaveError, ConflictError):
    """Exception related to an already existing item save."""

    def __init__(self, *, user_id: int, item_id: int):
        message = f"Item #{item_id} is already saved by user #{user_id}."

        super().__init__(message)


class ItemSaveNotExistsError(ItemSaveError, ConflictError):
    """Exception related to a non-existing item save."""

    def __init__(self, *, user_id: int, item_id: int):
        message = f"Item #{item_id} is not saved by user #{user_id}."

        super().__init__(message)
