from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.loan.query import (
    LoanRequestQueryPageCursor,
    LoanRequestReadQueryFilter,
)
from app.schemas.loan.read import LoanRequestRead
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_loan_request(
    db: Session,
    loan_request_id: int,
    query_filter: LoanRequestReadQueryFilter | None = None,
) -> LoanRequestRead:
    """Get loan request with `loan_request_id`."""

    # get loan request from database
    loan_request = database.loan.get_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=query_filter,
    )

    return LoanRequestRead.model_validate(loan_request)


def list_loan_requests(
    db: Session,
    *,
    query_filter: LoanRequestReadQueryFilter | None = None,
    page_options: QueryPageOptions | None = None,
) -> QueryPageResult[LoanRequestRead, LoanRequestQueryPageCursor]:
    """List the loan requests matching criteria."""

    # search loan requests in database
    result = database.loan.list_loan_requests(
        db=db,
        query_filter=query_filter,
        page_options=page_options,
    )

    return QueryPageResult[LoanRequestRead, LoanRequestQueryPageCursor](
        data=[LoanRequestRead.model_validate(loan) for loan in result.data],
        next_page_cursor=result.next_page_cursor,
    )
