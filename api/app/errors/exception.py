from datetime import datetime
from http import HTTPStatus
from typing import Any, Mapping, Optional
from app.enums import LoanRequestState


class ApiError(Exception):
    """Exception related to the API."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        creation_date: Optional[datetime] = None,
    ):
        if creation_date is None:
            creation_date = datetime.now()

        self.message = message
        self.status_code = status_code
        self.creation_date = creation_date

        super().__init__(message)


class NotFoundError(ApiError):
    """Exception raised when something is not found."""

    def __init__(
        self,
        *,
        datatype: str,
        key: Mapping[str, Any],
        **kwargs,
    ):
        super().__init__(
            message=f"{datatype.capitalize()} with {key!r} not found.",
            **kwargs,
        )


class ItemError(ApiError):
    """Exception related to an item."""

    pass


class ItemNotFoundError(NotFoundError, ItemError):
    """Exception raised when an item is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="item",
            key=key,
        )


class LoanRequestError(ApiError):
    """Exception related to a loan request."""

    pass


class LoanRequestNotFoundError(NotFoundError, LoanRequestError):
    """Exception raised when a loan request is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="loan request",
            key=key,
        )


class LoanRequestStateError(LoanRequestError):
    def __init__(
        self,
        *,
        expected_state: LoanRequestState,
        actual_state: LoanRequestState,
    ):
        super().__init__(
            message=(
                f"Loan request state is expected to be {expected_state.name!r}, "
                f"got: {actual_state.name!r}."
            ),
            status_code=HTTPStatus.BAD_REQUEST,
        )


class LoanError(ApiError):
    """Exception related to a loan."""

    pass


class LoanNotFoundError(NotFoundError, LoanError):
    """Exception raised when a loan is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="loan",
            key=key,
        )


class LoanAlreadyInactiveError(LoanError):
    def __init__(self):
        super().__init__(
            message="Loan is already inactive.",
            status_code=HTTPStatus.BAD_REQUEST,
        )


class ChatError(ApiError):
    """Exception related to a chat."""

    pass


class ChatNotFoundError(NotFoundError, ChatError):
    """Exception raised when a chat is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="chat",
            key=key,
        )


class ChatMessageError(ApiError):
    """Exception related to a chat message."""

    pass


class ChatMessageNotFoundError(NotFoundError, ChatMessageError):
    """Exception raised when a chat message is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="chat message",
            key=key,
        )


class UserError(ApiError):
    """Exception related to a user."""

    pass


class UserNotFoundError(NotFoundError, UserError):
    """Exception raised when a user is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="user",
            key=key,
        )


class RegionError(Exception):
    """Exception related to a region."""

    pass


class RegionNotFoundError(NotFoundError, RegionError):
    """Exception raised when a region is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="region",
            key=key,
        )


class ItemImageError(ApiError):
    """Exception related to an item image."""

    pass


class ItemImageNotFoundError(NotFoundError, ItemImageError):
    """Exception raised when an item image is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="image",
            key=key,
        )


class ItemLikeError(ApiError):
    """Exception related to a item like."""

    pass


class ItemLikeAlreadyExistsError(ApiError):
    """Exception related to an already existing item like."""

    def __init__(self, *, user_id: int, item_id: int):
        message = f"Item #{item_id} is already liked by user #{user_id}."

        super().__init__(
            message=message,
            status_code=HTTPStatus.CONFLICT,
        )


class ItemLikeNotExistsError(ApiError):
    """Exception related to a non-existing item like."""

    def __init__(self, *, user_id: int, item_id: int):
        message = f"Item #{item_id} is not liked by user #{user_id}."

        super().__init__(
            message=message,
            status_code=HTTPStatus.CONFLICT,
        )


class ItemSaveError(ApiError):
    """Exception related to a item save."""

    pass


class ItemSaveAlreadyExistsError(ApiError):
    """Exception related to an already existing item save."""

    def __init__(self, *, user_id: int, item_id: int):
        message = f"Item #{item_id} is already saved by user #{user_id}."

        super().__init__(
            message=message,
            status_code=HTTPStatus.CONFLICT,
        )


class ItemSaveNotExistsError(ApiError):
    """Exception related to a non-existing item save."""

    def __init__(self, *, user_id: int, item_id: int):
        message = f"Item #{item_id} is not saved by user #{user_id}."

        super().__init__(
            message=message,
            status_code=HTTPStatus.CONFLICT,
        )
