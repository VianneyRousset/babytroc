from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.loan.query import LoanQueryFilter, LoanRequestQueryFilter
from app.schemas.loan.read import LoanRead, LoanRequestRead
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_loan_request(
    db: Session,
    loan_request_id: int,
    query_filter: LoanRequestQueryFilter | None = None,
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
    query_filter: LoanRequestQueryFilter | None = None,
    page_options: QueryPageOptions | None = None,
) -> QueryPageResult[LoanRequestRead]:
    """List the loan requests matching criteria."""

    # search loan requests in database
    result = database.loan.list_loan_requests(
        db=db,
        query_filter=query_filter,
        page_options=page_options,
    )

    return QueryPageResult[LoanRequestRead].model_validate(result)


def get_loan(
    db: Session,
    loan_id: int,
    query_filter: LoanQueryFilter | None = None,
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
    query_filter: LoanQueryFilter | None = None,
    page_options: QueryPageOptions | None = None,
) -> QueryPageResult[LoanRead]:
    """List the loans matching criteria."""

    # search loan in database
    result = database.loan.list_loans(
        db=db,
        query_filter=query_filter,
        page_options=page_options,
    )

    return QueryPageResult[LoanRead].model_validate(result)
