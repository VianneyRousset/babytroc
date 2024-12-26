from typing import Any, Generic, Optional

from sqlalchemy import Select

from app.enums import LoanRequestState
from app.models.loan import Loan, LoanRequest
from app.models.user import User
from app.schemas.base import (
    QueryFilterBase,
    QueryPageOptionsBase,
    QueryPageResultBase,
    ResultType,
)


class LoanRequestQueryFilter(QueryFilterBase):
    """Filter of the loan requests query."""

    item_id: Optional[int] = None
    borrower_id: Optional[int] = None
    owner_id: Optional[int] = None
    state: Optional[LoanRequestState] = None

    def apply(self, stmt: Select) -> Select:
        """Apply filtering."""

        # filter item_id
        if self.item_id is not None:
            stmt = stmt.where(LoanRequest.item_id == self.item_id)

        # filter borrower_id
        if self.borrower_id is not None:
            stmt = stmt.where(Loan.borrower_id == self.borrower_id)

        # filter owner_id
        if self.owner_id is not None:
            stmt = stmt.join(User).where(User.id == self.owner_id)

        # filter state
        if self.state is not None:
            stmt = stmt.where(LoanRequest.state == self.state)

        return stmt

    @property
    def key(self) -> dict[str, Any]:
        return self.dict(exclude_none=True)


class LoanRequestQueryPageOptions(QueryPageOptionsBase):
    """Options on the queried page of loan requests."""

    limit: Optional[int] = None
    loan_request_id_lt: Optional[int] = None

    def apply(self, stmt: Select) -> Select:
        """Apply filtering."""


class LoanRequestQueryPageResult(QueryPageResultBase, Generic[ResultType]):
    """Info on the result page of loan requests."""

    query_filter: LoanRequestQueryFilter
    page_options: LoanRequestQueryPageOptions

    @property
    def min_loan_request_id(self) -> int | None:
        if self.loan_requests:
            return min(req.id for req in self.loan_requests)
        return None

    @classmethod
    def from_orm(
        cls,
        *,
        loan_requests: list[LoanRequest],
        query_filter: LoanRequestQueryFilter,
        page_options: LoanRequestQueryPageOptions,
    ):
        return cls(
            data=loan_requests,
            query_filter=query_filter,
            page_options=page_options,
        )


class LoanQueryFilter(QueryFilterBase):
    """Filter of the loans query."""

    item_id: Optional[int] = None
    borrower_id: Optional[int] = None
    owner_id: Optional[int] = None
    active: Optional[bool] = None


class LoanQueryPageOptions(QueryPageOptionsBase):
    """Options on the queried page of loans."""

    limit: Optional[int] = None
    loan_id: Optional[int] = None


class LoanQueryPageResult(QueryPageResultBase, Generic[ResultType]):
    """Info on the result page of loans."""

    query_filter: LoanQueryFilter
    page_options: LoanQueryPageOptions

    @property
    def min_loan_id(self) -> int | None:
        if self.loans:
            return min(loan.id for loan in self.loans)
        return None

    @classmethod
    def from_orm(
        cls,
        *,
        loans: list[Loan],
        query_filter: LoanQueryFilter,
        page_options: LoanQueryPageOptions,
    ):
        return cls(
            data=loans,
            query_filter=query_filter,
            page_options=page_options,
        )
