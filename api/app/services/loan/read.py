from typing import Optional

from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.loan.query import (
    LoanQueryFilter,
    LoanQueryPageOptions,
    LoanQueryPageResult,
    LoanRequestQueryFilter,
    LoanRequestQueryPageOptions,
    LoanRequestQueryPageResult,
)
from app.schemas.loan.read import LoanRead, LoanRequestRead


def get_loan_request(
    db: Session,
    loan_request_id: int,
    query_filter: Optional[LoanRequestQueryFilter] = None,
) -> LoanRequestRead:
    """Get loan request with `loan_request_id`."""

    # get loan request from database
    loan_request = database.loan.get_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=query_filter,
    )

    return LoanRequestRead.from_orm(loan_request)


def list_loan_requests(
    db: Session,
    *,
    query_filter: Optional[LoanRequestQueryFilter] = None,
    page_options: Optional[LoanRequestQueryPageOptions] = None,
) -> LoanRequestQueryPageResult[LoanRequestRead]:
    """List the loan requests matching criteria."""

    # search loan requests in database
    result = database.loan.list_loan_requests(
        db=db,
        query_filter=query_filter,
        page_options=page_options,
    )

    return LoanRequestQueryPageResult[LoanRequestRead].from_orm(result, LoanRequestRead)


def get_loan(
    db: Session,
    loan_id: int,
    query_filter: Optional[LoanQueryFilter] = None,
) -> LoanRead:
    """Get loan with `loan_id`."""

    # get loan from database
    loan = database.loan.get_loan(
        db=db,
        loan_id=loan_id,
        query_filter=query_filter,
    )

    return LoanRead.from_orm(loan)


def list_loans(
    db: Session,
    *,
    query_filter: Optional[LoanQueryFilter] = None,
    page_options: Optional[LoanQueryPageOptions] = None,
) -> LoanQueryPageResult[LoanRead]:
    """List the loans matching criteria."""

    # search loan in database
    result = database.loan.list_loans(
        db=db,
        query_filter=query_filter,
        page_options=page_options,
    )

    return LoanQueryPageResult[LoanRead].from_orm(result, LoanRead)
