from collections.abc import Collection, Mapping
from typing import Any

from app.enums import LoanRequestState
from app.schemas.loan.base import ItemBorrowerId

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
        expected_state: LoanRequestState | Collection[LoanRequestState],
        actual_state: LoanRequestState,
    ):
        expected = (
            " or ".join(repr(state.name) for state in expected_state)
            if isinstance(expected_state, Collection)
            else repr(expected_state.name)
        )

        super().__init__(
            message=(
                f"Loan request state is expected to be {expected}, "
                f"got: {actual_state.name!r}."
            ),
        )


class LoanRequestAlreadyExistsError(LoanRequestError, ConflictError):
    def __init__(self, item_borrower_id: ItemBorrowerId | set[ItemBorrowerId]):
        super().__init__(
            "Loan request already exists. Loan requests (item_id, borrower_id): "
            f"{item_borrower_id}."
        )


class LoanRequestOwnItemError(LoanRequestError, BadRequestError):
    def __init__(self, item_id: int):
        super().__init__(
            "Cannot add loan request where the borrower is also the owner "
            f"(item {item_id})."
        )
