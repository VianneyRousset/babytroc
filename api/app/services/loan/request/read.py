from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.loan import LoanRequestNotFoundError
from app.models.loan import LoanRequest
from app.schemas.loan.query import (
    LoanRequestQueryPageCursor,
    LoanRequestReadQueryFilter,
)
from app.schemas.loan.read import LoanRequestRead
from app.schemas.query import QueryPageOptions, QueryPageResult


async def get_loan_request(
    db: AsyncSession,
    loan_request_id: int | None = None,
    *,
    query_filter: LoanRequestReadQueryFilter | None = None,
) -> LoanRequestRead:
    """Get loan request with `loan_request_id`."""

    loan_requests = get_many_loan_requests(
        db=db,
        loan_request_ids={loan_request_id},
        query_filter=query_filter,
    )

    return loan_requests[0]


async def get_many_loan_requests(
    db: AsyncSession,
    loan_request_ids: set[int],
    *,
    query_filter: LoanRequestReadQueryFilter | None = None,
) -> list[LoanRequestRead]:
    """Get all loan requests with the given loan request ids.

    Raises LoanRequestNotFoundError if not all loan requests matching criterias exist.
    """

    # default query filter
    query_filter = query_filter or LoanRequestReadQueryFilter()

    stmt = query_filter.filter_read(
        select(LoanRequest).where(LoanRequest.id.in_(loan_request_ids))
    )

    loan_requests = (await db.execute(stmt)).unique().scalars().all()

    missing_loan_request_ids = loan_request_ids - {req.id for req in loan_requests}
    if missing_loan_request_ids:
        key = query_filter.key | {"loan_request_ids": missing_loan_request_ids}
        raise LoanRequestNotFoundError(key)

    return [LoanRequestRead.model_validate(req) for req in loan_requests]


async def list_loan_requests(
    db: AsyncSession,
    *,
    query_filter: LoanRequestReadQueryFilter | None = None,
    page_options: QueryPageOptions | None = None,
) -> QueryPageResult[LoanRequestRead, LoanRequestQueryPageCursor]:
    """List the loan requests matching criteria."""

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

    loan_requests = list((await db.execute(stmt)).scalars().all())

    return QueryPageResult[LoanRequestRead, LoanRequestQueryPageCursor](
        data=[LoanRequestRead.model_validate(req) for req in loan_requests],
        next_page_cursor=LoanRequestQueryPageCursor(
            loan_request_id=loan_requests[-1].id,
        )
        if loan_requests
        else None,
    )
