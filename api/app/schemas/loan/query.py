from typing import Any, Generic, Optional

from sqlalchemy import Select, func

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
        # apply limit
        if self.limit is not None:
            stmt = stmt.limit(self.limit)

        # if loan_request_id_lt is provided, add it to the query
        if self.loan_request_id_lt is not None:
            stmt = stmt.where(LoanRequest.id < self.loan_request_id_lt)

        return stmt


class LoanRequestQueryPageResult(QueryPageResultBase, Generic[ResultType]):
    """Info on the result page of loan requests."""

    query_filter: LoanRequestQueryFilter
    page_options: LoanRequestQueryPageOptions

    @property
    def min_loan_request_id(self) -> int | None:
        if self.loan_requests:
            return min(req.id for req in self.loan_requests)
        return None


class LoanQueryFilter(QueryFilterBase):
    """Filter of the loans query."""

    item_id: Optional[int] = None
    borrower_id: Optional[int] = None
    owner_id: Optional[int] = None
    active: Optional[bool] = None

    def apply(self, stmt: Select) -> Select:
        """Apply filtering."""

        # filter item_id
        if self.item_id is not None:
            stmt = stmt.where(Loan.item_id == self.item_id)

        # filter borrower_id
        if self.borrower_id is not None:
            stmt = stmt.where(Loan.borrower_id == self.borrower_id)

        # filter owner_id
        if self.owner_id is not None:
            stmt = stmt.join(User).where(User.id == self.owner_id)

        # filter state
        if self.active is not None:
            stmt = stmt.where(func.upper_inf(Loan.during))

        return stmt


class LoanQueryPageOptions(QueryPageOptionsBase):
    """Options on the queried page of loans."""

    limit: Optional[int] = None
    loan_id_lt: Optional[int] = None

    def apply(self, stmt: Select) -> Select:
        """Apply pagination options."""

        # apply limit
        if self.limit is not None:
            stmt = stmt.limit(self.limit)

        # filter loan_id_lt
        if self.loan_id_lt is not None:
            stmt = stmt.where(Loan.id < self.loan_id_lt)

        return stmt


class LoanQueryPageResult(QueryPageResultBase, Generic[ResultType]):
    """Info on the result page of loans."""

    query_filter: LoanQueryFilter
    page_options: LoanQueryPageOptions

    @property
    def min_loan_id(self) -> int | None:
        if self.loans:
            return min(loan.id for loan in self.loans)
        return None
