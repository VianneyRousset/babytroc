from typing import Annotated

from app.enums import LoanRequestState
from app.schemas.base import ApiQueryBase, FieldWithAlias, PageLimitField
from app.schemas.query import QueryPageOptions

from .query import (
    LoanQueryPageCursor,
    LoanReadQueryFilter,
    LoanRequestQueryPageCursor,
    LoanRequestReadQueryFilter,
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
    def loan_request_select_query_filter(self) -> LoanRequestReadQueryFilter:
        return LoanRequestReadQueryFilter(
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

        if self.active:
            return LoanRequestState.get_active_states()

        return LoanRequestState.get_inactive_states()


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
    def loan_select_query_filter(self) -> LoanReadQueryFilter:
        return LoanReadQueryFilter(
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
