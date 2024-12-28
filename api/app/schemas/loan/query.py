from typing import Optional

from sqlalchemy import Select, func

from app.enums import LoanRequestState
from app.models.loan import Loan, LoanRequest
from app.models.user import User
from app.schemas.base import QueryFilterBase


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
