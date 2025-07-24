from typing import Annotated

from app.enums import LoanRequestState
from app.schemas.base import ApiQueryBase, FieldWithAlias, PageLimitField
from app.schemas.query import QueryPageOptions

from .query import (
    LoanQueryFilter,
    LoanQueryPageCursor,
    LoanRequestQueryFilter,
    LoanRequestQueryPageCursor,
)


class LoanRequestApiQuery(ApiQueryBase, LoanRequestQueryPageCursor):
    # active
    active: Annotated[
        bool | None,
        FieldWithAlias(
            name="active",
            alias="a",
            title="Active loan requests",
            description="Only return pending and accepted loan requests.",
        ),
    ] = None

    limit: Annotated[int, PageLimitField()] = 32

    @property
    def loan_request_query_filter(self) -> LoanRequestQueryFilter:
        return LoanRequestQueryFilter(
            states=self.loan_request_query_filter_states,
        )

    @property
    def loan_request_query_page_cursor(self) -> LoanRequestQueryPageCursor:
        return LoanRequestQueryPageCursor(
            loan_request_id=self.loan_request_id,
        )

    @property
    def loan_request_query_page_options(
        self,
    ) -> QueryPageOptions[LoanRequestQueryPageCursor]:
        return QueryPageOptions[LoanRequestQueryPageCursor](
            limit=self.limit,
            cursor=self.loan_request_query_page_cursor,
        )

        return LoanRequestQueryPageCursor(
            loan_request_id=self.loan_request_id,
        )

    @property
    def loan_request_query_filter_states(self) -> None | set[LoanRequestState]:
        if self.active is None:
            return None

        active_states = {LoanRequestState.pending, LoanRequestState.accepted}

        if self.active:
            return active_states

        return set(LoanRequestState) - active_states


class LoanApiQuery(LoanQueryPageCursor):
    # active
    active: Annotated[
        bool | None,
        FieldWithAlias(
            name="active",
            alias="a",
            title="Active loan",
            description="Only return active loans.",
        ),
    ] = None

    limit: Annotated[int, PageLimitField()] = 32

    @property
    def loan_query_filter(self) -> LoanQueryFilter:
        return LoanQueryFilter(
            active=self.active,
        )

    @property
    def loan_query_page_cursor(self) -> LoanQueryPageCursor:
        return LoanQueryPageCursor(
            loan_id=self.loan_id,
        )

    @property
    def loan_query_page_options(
        self,
    ) -> QueryPageOptions[LoanQueryPageCursor]:
        return QueryPageOptions[LoanQueryPageCursor](
            limit=self.limit,
            cursor=self.loan_query_page_cursor,
        )

        return LoanQueryPageCursor(
            loan_id=self.loan_id,
        )
