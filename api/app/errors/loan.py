from collections.abc import Mapping
from typing import Any

from app.enums import LoanRequestState

from .base import ApiError, BadRequestError, ConflictError, NotFoundError


class LoanError(ApiError):
    """Exception related to a loan."""

    pass


class LoanNotFoundError(LoanError, NotFoundError):
    """Exception raised when a loan is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="loan",
            key=key,
        )


class LoanAlreadyInactiveError(LoanError, ConflictError):
    def __init__(self):
        super().__init__(
            message="Loan is already inactive.",
        )


class LoanRequestError(ApiError):
    """Exception related to a loan request."""

    pass


class LoanRequestNotFoundError(LoanRequestError, NotFoundError):
    """Exception raised when a loan request is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="loan request",
            key=key,
        )


class LoanRequestStateError(LoanRequestError, ConflictError):
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
        )


class LoanRequestAlreadyExistsError(LoanRequestError, ConflictError):
    def __init__(self):
        super().__init__("Loan request already exists.")


class LoanRequestOwnItemError(LoanRequestError, BadRequestError):
    def __init__(self):
        super().__init__(
            "Cannot add loan request where the borrower is also the owner."
        )
