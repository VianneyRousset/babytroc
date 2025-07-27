from sqlalchemy import desc, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.loan import LoanRequestNotFoundError
from app.models.loan import LoanRequest
from app.schemas.loan.query import (
    LoanRequestQueryPageCursor,
    LoanRequestReadQueryFilter,
)
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_loan_request(
    db: Session,
    loan_request_id: int | None = None,
    *,
    query_filter: LoanRequestReadQueryFilter | None = None,
) -> LoanRequest:
    """Get loan request with ID `loan_request_id`."""

    # default query filter
    query_filter = query_filter or LoanRequestReadQueryFilter()

    stmt = select(LoanRequest)

    if loan_request_id is not None:
        stmt = stmt.where(LoanRequest.id == loan_request_id)

    stmt = query_filter.filter_read(stmt)

    try:
        req = db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": loan_request_id}
        raise LoanRequestNotFoundError(key) from error

    return req


def list_loan_requests(
    db: Session,
    *,
    query_filter: LoanRequestReadQueryFilter | None = None,
    page_options: QueryPageOptions | None = None,
) -> QueryPageResult[LoanRequest, LoanRequestQueryPageCursor]:
    """List loan requests matching criteria."""

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or LoanRequestReadQueryFilter()

    # if no page options are provided, use default page options
    page_options = page_options or QueryPageOptions(
        cursor=LoanRequestQueryPageCursor(),
    )

    # selection
    stmt = select(LoanRequest)

    # apply filtering
    stmt = query_filter.filter_read(stmt)

    # apply ordering
    stmt = stmt.order_by(desc(LoanRequest.id))

    # apply pagination
    stmt = stmt.limit(page_options.limit)
    if page_options.cursor.loan_request_id is not None:
        stmt = stmt.where(LoanRequest.id < page_options.cursor.loan_request_id)

    loan_requests = list(db.execute(stmt).scalars().all())

    return QueryPageResult[LoanRequest, LoanRequestQueryPageCursor](
        data=loan_requests,
        next_page_cursor=LoanRequestQueryPageCursor(
            loan_request_id=loan_requests[-1].id,
        )
        if loan_requests
        else None,
    )
