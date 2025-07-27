from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.loan.query import LoanQueryPageCursor, LoanReadQueryFilter
from app.schemas.loan.read import LoanRead
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_loan(
    db: Session,
    loan_id: int,
    query_filter: LoanReadQueryFilter | None = None,
) -> LoanRead:
    """Get loan with `loan_id`."""

    # get loan from database
    loan = database.loan.get_loan(
        db=db,
        loan_id=loan_id,
        query_filter=query_filter,
    )

    return LoanRead.model_validate(loan)


def list_loans(
    db: Session,
    *,
    query_filter: LoanReadQueryFilter | None = None,
    page_options: QueryPageOptions | None = None,
) -> QueryPageResult[LoanRead, LoanQueryPageCursor]:
    """List the loans matching criteria."""

    # search loan in database
    result = database.loan.list_loans(
        db=db,
        query_filter=query_filter,
        page_options=page_options,
    )

    return QueryPageResult[LoanRead, LoanQueryPageCursor](
        data=[LoanRead.model_validate(loan) for loan in result.data],
        next_page_cursor=result.next_page_cursor,
    )
