from sqlalchemy import Select, func

from app.enums import LoanRequestState
from app.models.item import Item
from app.models.loan import Loan, LoanRequest
from app.schemas.base import QueryFilterBase


class LoanRequestQueryFilter(QueryFilterBase):
    """Filter of the loan requests query."""

    item_id: int | None = None
    borrower_id: int | None = None
    owner_id: int | None = None
    states: set[LoanRequestState] | None = None

    def apply(self, stmt: Select) -> Select:
        """Apply filtering."""

        # filter item_id
        if self.item_id is not None:
            stmt = stmt.where(LoanRequest.item_id == self.item_id)

        # filter borrower_id
        if self.borrower_id is not None:
            stmt = stmt.where(LoanRequest.borrower_id == self.borrower_id)

        # filter owner_id
        if self.owner_id is not None:
            stmt = stmt.join(Item).where(Item.owner_id == self.owner_id)

        # filter state
        if self.states is not None:
            stmt = stmt.filter(LoanRequest.state.in_(self.states))

        return stmt


class LoanQueryFilter(QueryFilterBase):
    """Filter of the loans query."""

    item_id: int | None = None
    borrower_id: int | None = None
    owner_id: int | None = None
    active: bool | None = None

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
            stmt = stmt.join(Item).where(Item.owner_id == self.owner_id)

        # filter state
        if self.active is not None:
            if self.active:
                stmt = stmt.where(func.upper_inf(Loan.during))
            else:
                stmt = stmt.where(func.upper(Loan.during).is_not(None))

        return stmt
