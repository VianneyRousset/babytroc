from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.exception import LoanNotFoundError, LoanRequestNotFoundError
from app.models.loan import Loan, LoanRequest
from app.schemas.loan.query import LoanQueryFilter, LoanRequestQueryFilter
from app.schemas.query import QueryPageOptions, QueryPageResult


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
    page_options: Optional[QueryPageOptions] = None,
) -> QueryPageResult[LoanRequest]:
    """List loan requests matching criteria."""

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or LoanRequestQueryFilter()

    # if no page options are provided, use default page options
    page_options = page_options or QueryPageOptions()

    stmt = select(LoanRequest)

    # apply filtering
    stmt = query_filter.apply(stmt)

    # apply pagination
    stmt = page_options.apply(
        stmt=stmt,
        columns={
            "loan_request_id": LoanRequest.id,
        },
    )

    loan_requests = (db.execute(stmt)).scalars().all()

    return QueryPageResult[LoanRequest](
        data=loan_requests,
        order={
            "loan_request_id": [req.id for req in loan_requests],
        },
        desc=page_options.desc,
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
    page_options: Optional[QueryPageOptions] = None,
) -> QueryPageResult[Loan]:
    """List items matching criteria."""

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or LoanQueryFilter()

    # if no page options are provided, use default page options
    page_options = page_options or QueryPageOptions()

    stmt = select(Loan)

    # apply filtering
    stmt = page_options.apply(stmt)

    # apply pagination
    stmt = query_filter.apply(
        stmt=stmt,
        columns={
            "loan_id": Loan.id,
        },
    )

    loans = (db.execute(stmt)).scalars().all()

    return QueryPageResult[Loan](
        data=loans,
        order={
            "loan_id": [loan.id for loan in loans],
        },
        desc=page_options.desc,
    )
