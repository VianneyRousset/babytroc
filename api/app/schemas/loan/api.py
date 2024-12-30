from typing import Optional

from pydantic import Field

from app.enums import LoanRequestState
from app.schemas.base import ApiQueryBase


class LoanRequestApiQuery(ApiQueryBase):
    # state
    state: Optional[LoanRequestState] = Field(
        title="State of the loan request",
        description="Only return loan requests in the given state.",
        default=None,
    )
    # limit
    n: Optional[int] = Field(
        title="Limit returned loan requests count",
        description="Limit the number of loan requests returned.",
        examples=[
            [42],
        ],
        gt=0,
        le=128,
        default=64,
    )

    # cursor loan_request_id
    cid: Optional[int] = Field(
        title="Page cursor for loan request ID",
        gt=0,
        default=None,
    )


class LoanApiQuery(ApiQueryBase):
    # item_id
    item: Optional[int] = Field(
        title="Loaned item",
        description="Only return loan with this item ID.",
        ge=0,
        default=None,
    )

    # active
    active: Optional[bool] = Field(
        title="Active",
        description="Only return active loans.",
        default=None,
    )

    # limit
    n: Optional[int] = Field(
        title="Limit returned loans count",
        description="Limit the number of loans returned.",
        examples=[
            [42],
        ],
        gt=0,
        le=128,
        default=64,
    )

    # cursor loan_request_id
    cid: Optional[int] = Field(
        title="Page cursor for loan ID",
        gt=0,
        default=None,
    )
