from sqlalchemy import desc, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.loan import LoanNotFoundError
from app.models.loan import Loan, LoanRequest
from app.schemas.loan.query import LoanQueryPageCursor, LoanReadQueryFilter
from app.schemas.query import QueryPageOptions, QueryPageResult


def get_loan(
    db: Session,
    loan_id: int,
    *,
    query_filter: LoanReadQueryFilter | None = None,
) -> Loan:
    """Get loan with ID `loan_id`."""

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or LoanReadQueryFilter()

    stmt = select(Loan).where(Loan.id == loan_id)

    stmt = query_filter.filter_read(stmt)

    try:
        return (db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"loan_id": loan_id}
        raise LoanNotFoundError(key) from error


def list_loans(
    db: Session,
    *,
    query_filter: LoanReadQueryFilter | None = None,
    page_options: QueryPageOptions | None = None,
) -> QueryPageResult[Loan, LoanQueryPageCursor]:
    """List items matching criteria."""

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or LoanReadQueryFilter()

    # if no page options are provided, use default page options
    page_options = page_options or QueryPageOptions(
        cursor=LoanQueryPageCursor(),
    )

    # selection
    stmt = select(Loan)

    # apply filtering
    stmt = query_filter.filter_read(stmt)

    # apply ordering
    stmt = stmt.order_by(desc(LoanRequest.id))

    # apply pagination
    stmt = stmt.limit(page_options.limit)
    if page_options.cursor.loan_id is not None:
        stmt = stmt.where(Loan.id < page_options.cursor.loan_id)

    loans = list(db.execute(stmt).scalars().all())

    return QueryPageResult[Loan, LoanQueryPageCursor](
        data=loans,
        next_page_cursor=LoanQueryPageCursor(
            loan_id=loans[-1].id,
        )
        if loans
        else None,
    )
