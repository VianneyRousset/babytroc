from typing import Annotated

from sqlalchemy import func, tuple_

from app.enums import LoanRequestState
from app.models.item import Item
from app.models.loan import Loan, LoanRequest
from app.schemas.base import (
    FieldWithAlias,
    Joins,
    QueryFilter,
    StatementT,
)
from app.schemas.loan.base import ItemBorrowerId
from app.schemas.query import QueryPageCursor


class LoanRequestQueryFilterItemBorrower(QueryFilter):
    """Filter loan requests by item."""

    item_borrower_id: set[ItemBorrowerId] | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        if self.item_borrower_id is None:
            return super()._filter(stmt)

        return super()._filter(
            stmt.where(
                tuple_(LoanRequest.item_id, LoanRequest.borrower_id).in_(
                    [
                        tuple_(
                            item_borrower_id.item_id,
                            item_borrower_id.borrower_id,
                        )
                        for item_borrower_id in self.item_borrower_id
                    ]
                )
            )
        )


class LoanRequestQueryFilterItem(QueryFilter):
    """Filter loan requests by item."""

    item_id: int | set[int] | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        if self.item_id is None:
            return super()._filter(stmt)

        if isinstance(self.item_id, set):
            return super()._filter(stmt.where(LoanRequest.item_id.in_(self.item_id)))

        return super()._filter(stmt.where(LoanRequest.item_id == self.item_id))


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


class LoanRequestQueryFilterOwner(QueryFilter):
    """Filter loan requests by owner."""

    owner_id: int | None = None

    @property
    def _joins(self) -> Joins:
        return super()._joins + ([Item] if self.owner_id is not None else [])

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(Item.owner_id == self.owner_id).where(
                Item.id == LoanRequest.item_id
            )
            if self.owner_id is not None
            else stmt
        )


class LoanRequestReadQueryFilter(
    LoanRequestQueryFilterItemBorrower,
    LoanRequestQueryFilterItem,
    LoanRequestQueryFilterStates,
    LoanRequestQueryFilterOwner,
    LoanRequestQueryFilterBorrower,
):
    """Filter of the loan requests read query."""


class LoanRequestUpdateQueryFilter(
    LoanRequestQueryFilterItemBorrower,
    LoanRequestQueryFilterItem,
    LoanRequestQueryFilterStates,
    LoanRequestQueryFilterOwner,
    LoanRequestQueryFilterBorrower,
):
    """Filter of the loan requests update query."""


class LoanRequestDeleteQueryFilter(
    LoanRequestQueryFilterItemBorrower,
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

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(Item.owner_id == self.owner_id).where(Item.id == Loan.item_id)
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
    LoanQueryFilterOwner,
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
