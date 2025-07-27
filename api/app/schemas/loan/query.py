from typing import Annotated

from sqlalchemy import Select, func

from app.enums import LoanRequestState
from app.models.item import Item
from app.models.loan import Loan, LoanRequest
from app.schemas.base import (
    FieldWithAlias,
    Joins,
    QueryFilter,
    ReadQueryFilter,
    StatementT,
)
from app.schemas.query import QueryPageCursor


class LoanRequestQueryFilterItem(QueryFilter):
    """Filter loan requests by item."""

    item_id: int | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(LoanRequest.item_id == self.item_id)
            if self.item_id is not None
            else stmt
        )


class LoanRequestQueryFilterStates(QueryFilter):
    """Filter loan requests by states."""

    states: set[LoanRequestState] | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(LoanRequest.state.in_(self.states))
            if self.states is not None
            else stmt
        )


class LoanRequestQueryFilterBorrower(QueryFilter):
    """Filter loan requests by borrower."""

    borrower_id: int | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(LoanRequest.borrower_id == self.borrower_id)
            if self.borrower_id is not None
            else stmt
        )


class LoanRequestQueryFilterOwner(ReadQueryFilter):
    """Filter loan requests by owner."""

    owner_id: int | None = None

    @property
    def _joins(self) -> Joins:
        return super()._joins + ([Item] if self.owner_id is not None else [])

    def _filter_read(self, stmt: Select) -> Select:
        return super()._filter_read(
            stmt.where(Item.owner_id == self.owner_id)
            if self.owner_id is not None
            else stmt
        )


class LoanRequestReadQueryFilter(
    LoanRequestQueryFilterItem,
    LoanRequestQueryFilterStates,
    LoanRequestQueryFilterOwner,
    LoanRequestQueryFilterBorrower,
):
    """Filter of the loan requests read query."""


class LoanRequestUpdateQueryFilter(
    LoanRequestQueryFilterItem,
    LoanRequestQueryFilterStates,
    LoanRequestQueryFilterBorrower,
):
    """Filter of the loan requests update query."""


class LoanRequestDeleteQueryFilter(
    LoanRequestQueryFilterItem,
    LoanRequestQueryFilterStates,
    LoanRequestQueryFilterBorrower,
):
    """Filter of the loan requests delete query."""


class LoanQueryFilterItem(QueryFilter):
    """Filter loan requests by item."""

    item_id: int | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(Loan.item_id == self.item_id)
            if self.item_id is not None
            else stmt
        )


class LoanQueryFilterActivity(QueryFilter):
    """Filter loan by activity."""

    active: bool | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        if self.active is not None:
            stmt = (
                stmt.where(func.upper_inf(Loan.during))
                if self.active
                else stmt.where(func.upper(Loan.during).is_not(None))
            )

        return super()._filter(stmt)


class LoanQueryFilterBorrower(QueryFilter):
    """Filter loan requests by borrower."""

    borrower_id: int | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(Loan.borrower_id == self.borrower_id)
            if self.borrower_id is not None
            else stmt
        )


class LoanQueryFilterOwner(QueryFilter):
    """Filter loan requests by owner."""

    owner_id: int | None = None

    @property
    def _joins(self) -> Joins:
        return super()._joins + ([Item] if self.owner_id is not None else [])

    def _filter_read(self, stmt: Select) -> Select:
        return super()._filter(
            stmt.where(Item.owner_id == self.owner_id)
            if self.owner_id is not None
            else stmt
        )


class LoanReadQueryFilter(
    LoanQueryFilterItem,
    LoanQueryFilterActivity,
    LoanQueryFilterOwner,
    LoanQueryFilterBorrower,
):
    """Filter of the loan read query."""


class LoanUpdateQueryFilter(
    LoanQueryFilterItem,
    LoanQueryFilterActivity,
    LoanQueryFilterBorrower,
):
    """Filter of the loan update query."""


class LoanDeleteQueryFilter(
    LoanQueryFilterItem,
    LoanQueryFilterActivity,
    LoanQueryFilterBorrower,
):
    """Filter of the loan delete query."""


class LoanRequestQueryPageCursor(QueryPageCursor):
    loan_request_id: Annotated[
        int | None,
        FieldWithAlias(
            name="loan_request_id",
            alias="cid",
        ),
    ] = None


class LoanQueryPageCursor(QueryPageCursor):
    loan_id: Annotated[
        int | None,
        FieldWithAlias(
            name="loan_id",
            alias="cid",
        ),
    ] = None
