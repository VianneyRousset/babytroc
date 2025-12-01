from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.errors.loan import LoanNotFoundError
from app.models.item import Item
from app.models.loan import Loan, LoanRequest
from app.schemas.loan.query import LoanQueryPageCursor, LoanReadQueryFilter
from app.schemas.loan.read import LoanRead
from app.schemas.query import QueryPageOptions, QueryPageResult


async def get_loan(
    db: AsyncSession,
    loan_id: int,
    *,
    query_filter: LoanReadQueryFilter | None = None,
) -> LoanRead:
    """Get loan with `loan_id`."""

    loans = await get_many_loans(
        db=db,
        loan_ids={loan_id},
        query_filter=query_filter,
    )

    return loans[0]


async def get_many_loans(
    db: AsyncSession,
    loan_ids: set[int],
    *,
    query_filter: LoanReadQueryFilter | None = None,
) -> list[LoanRead]:
    """Get all loans with the given loan ids.

    Raises LoanNotFoundError if not all loans matching criterias exist.
    """

    # if no query filter is provided, use an empty filter
    query_filter = query_filter or LoanReadQueryFilter()

    stmt = query_filter.filter_read(select(Loan).where(Loan.id.in_(loan_ids)))

    stmt = stmt.options(
        # loan -> borrower
        selectinload(Loan.borrower),
        # loan -> item -> owner
        selectinload(Loan.item).selectinload(Item.owner),
        # loan -> item -> first_image_name
        selectinload(Loan.item).undefer(Item.first_image_name),
        # loan -> item -> first_image_name
        selectinload(Loan.loan_request).selectinload(LoanRequest.borrower),
        # loan -> loan_request -> item -> first_image_name
        selectinload(Loan.loan_request)
        .selectinload(LoanRequest.item)
        .undefer(Item.first_image_name),
    )

    res = await db.execute(stmt)
    loans = res.unique().scalars().all()

    missing_loan_ids = loan_ids - {loan.id for loan in loans}
    if missing_loan_ids:
        key = query_filter.key | {"loan_ids": missing_loan_ids}
        raise LoanNotFoundError(key)

    return [LoanRead.model_validate(loan) for loan in loans]


async def list_loans(
    db: AsyncSession,
    *,
    query_filter: LoanReadQueryFilter | None = None,
    page_options: QueryPageOptions | None = None,
) -> QueryPageResult[LoanRead, LoanQueryPageCursor]:
    """List the loans matching criteria."""

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
    stmt = stmt.order_by(desc(Loan.id))

    # apply pagination
    stmt = stmt.limit(page_options.limit)
    if page_options.cursor.loan_id is not None:
        stmt = stmt.where(Loan.id < page_options.cursor.loan_id)

    stmt = stmt.options(
        # loan -> borrower
        selectinload(Loan.borrower),
        # loan -> item -> owner
        selectinload(Loan.item).selectinload(Item.owner),
        # loan -> item -> first_image_name
        selectinload(Loan.item).undefer(Item.first_image_name),
        # loan -> item -> first_image_name
        selectinload(Loan.loan_request).selectinload(LoanRequest.borrower),
        # loan -> loan_request -> item -> first_image_name
        selectinload(Loan.loan_request)
        .selectinload(LoanRequest.item)
        .undefer(Item.first_image_name),
    )

    loans = list((await db.execute(stmt)).scalars().all())

    return QueryPageResult[LoanRead, LoanQueryPageCursor](
        data=[LoanRead.model_validate(loan) for loan in loans],
        next_page_cursor=LoanQueryPageCursor(
            loan_id=loans[-1].id,
        )
        if loans
        else None,
    )
