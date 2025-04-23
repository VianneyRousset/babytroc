
from pydantic import Field

from app.enums import LoanRequestState
from app.schemas.base import ApiQueryBase


class LoanRequestApiQuery(ApiQueryBase):
    # state
    state: LoanRequestState | None = Field(
        title="State of the loan request",
        description="Only return loan requests in the given state.",
        default=LoanRequestState.pending,
    )


class LoanApiQuery(ApiQueryBase):
    # item_id
    item: int | None = Field(
        title="Loaned item",
        description="Only return loan with this item ID.",
        ge=0,
        default=None,
    )

    # active
    active: bool | None = Field(
        title="Active",
        description="Only return active loans.",
        default=None,
    )
