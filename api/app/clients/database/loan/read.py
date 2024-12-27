from collections.abc import Collection
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.exception import LoanNotFoundError, LoanRequestNotFoundError
from app.models.loan import Loan, LoanRequest
from app.schemas.loan.query import (
    LoanQueryFilter,
    LoanQueryPageOptions,
    LoanQueryPageResult,
    LoanRequestQueryFilter,
    LoanRequestQueryPageOptions,
    LoanRequestQueryPageResult,
)


def get_loan_request(
    db: Session,
    loan_request_id: int,
    *,
    query_filter: Optional[LoanRequestQueryFilter] = None,
) -> LoanRequest:
    """Get loan request with ID `loan_request_id`."""

    # default query filter
    query_filter = query_filter or LoanRequestQueryFilter()

    stmt = select(LoanRequest).where(LoanRequest.id == loan_request_id)

    stmt = query_filter.apply(stmt)

    try:
        return (db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": loan_request_id}
        raise LoanRequestNotFoundError(key) from error


def list_loan_requests(
    db: Session,
    *,
    query_filter: Optional[LoanRequestQueryFilter] = None,
    page_options: Optional[LoanRequestQueryPageOptions] = None,
) -> LoanRequestQueryPageResult[LoanRequest]:
    """List loan requests matching criteria.

    Order
    -----
    The loan requests are returned sorted by decreasing `loan_request_id`.
    """

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or LoanRequestQueryFilter()

    # if no page options are provided, use default page options
    page_options = page_options or LoanRequestQueryPageOptions()

    stmt = select(LoanRequest)

    stmt = query_filter.apply(stmt)
    stmt = page_options.apply(stmt)

    stmt = stmt.order_by(LoanRequest.id.desc())

    loan_requests = (db.execute(stmt)).scalars().all()

    return LoanRequestQueryPageResult[LoanRequest](
        data=loan_requests,
        query_filter=query_filter,
        page_options=page_options,
    )


def get_loan(
    db: Session,
    loan_id: int,
    *,
    query_filter: Optional[LoanQueryFilter] = None,
) -> Loan:
    """Get loan with ID `loan_id`."""

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or LoanQueryFilter()

    stmt = select(Loan).where(Loan.id == loan_id)

    stmt = query_filter.apply(stmt)

    try:
        return (db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"loan_id": loan_id}
        raise LoanNotFoundError(key) from error


def list_loans(
    db: Session,
    *,
    query_filter: Optional[LoanQueryFilter] = None,
    page_options: Optional[LoanQueryPageOptions] = None,
) -> LoanQueryPageResult[Loan]:
    """List items matching criteria.

    Order
    -----
    The loans are returned sorted by decreasing `loan_id`.
    """

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or LoanQueryFilter()

    # if no page options are provided, use default page options
    page_options = page_options or LoanQueryPageOptions()

    stmt = select(Loan)

    stmt = page_options.apply(stmt)
    stmt = query_filter.apply(stmt)

    stmt = stmt.order_by(Loan.id.desc())

    loans = (db.execute(stmt)).scalars().all()

    return LoanQueryPageResult[Loan](
        data=loans,
        query_filter=query_filter,
        page_options=page_options,
    )
