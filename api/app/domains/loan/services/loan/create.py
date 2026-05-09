from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.loan.enums import LoanRequestState
from app.domains.loan.events import LoanStarted
from app.domains.loan.models import Loan, LoanRequest
from app.domains.loan.schemas.query import LoanRequestUpdateQueryFilter
from app.domains.loan.schemas.read import LoanRead
from app.domains.loan.services.loan.read import get_many_loans
from app.domains.loan.services.request.update import update_many_loan_requests_state
from app.infrastructure.events import emit


async def execute_loan_request(
    db: AsyncSession,
    *,
    loan_request_id: int,
    query_filter: LoanRequestUpdateQueryFilter | None = None,
    check_state: bool = True,
) -> LoanRead:
    """Create a loan from the given loan request.

    Loan request state must be `accepted` if `check_state` is `True`.

    The loan request state is changed to `executed`.
    """

    loans = await execute_many_loan_requests(
        db=db,
        loan_request_ids={loan_request_id},
        query_filter=query_filter,
        check_state=check_state,
    )

    return loans[0]


async def execute_many_loan_requests(
    db: AsyncSession,
    *,
    loan_request_ids: set[int],
    query_filter: LoanRequestUpdateQueryFilter | None = None,
    check_state: bool = True,
    send_messages: bool = True,
) -> list[LoanRead]:
    """Create a loan from each given loan request id.

    Loan request states must be `accepted` if `check_state` is `True`.

    The loan requests states are changed to `executed`.
    """

    query_filter = query_filter or LoanRequestUpdateQueryFilter()

    # only update accepted loan requests
    # the number of updated loan requests are then checked against the given ids
    # to ensure not state were different than `accepted`
    if check_state:
        query_filter.states = (query_filter.states or set()) | {
            LoanRequestState.accepted
        }

    # update state
    await update_many_loan_requests_state(
        db=db,
        loan_request_ids=loan_request_ids,
        state=LoanRequestState.executed,
        query_filter=query_filter,
    )

    # insert loan for each given loan request and set the `loan_request_id` field for
    # each new loan
    create_loans_stmt = (
        insert(Loan)
        .from_select(
            [Loan.item_id, Loan.borrower_id, Loan.loan_request_id],  # type: ignore[list-item]
            select(LoanRequest.item_id, LoanRequest.borrower_id, LoanRequest.id).where(
                LoanRequest.id.in_(loan_request_ids)
            ),
        )
        .returning(Loan)
    )

    res = await db.execute(create_loans_stmt)
    loans = res.unique().scalars().all()

    # check the number of created loans matched the number of given loan requests
    if len(loans) != len(loan_request_ids):
        msg = (
            "The number of created loans does not match the number of given "
            "loan request ids. The reason is unexpected."
        )
        raise RuntimeError(msg)

    loan_reads = await get_many_loans(
        db=db,
        loan_ids={loan.id for loan in loans},
    )

    # emit events
    if send_messages:
        for loan_read in loan_reads:
            await emit(
                db,
                LoanStarted(
                    loan_id=loan_read.id,
                    loan_request_id=loan_read.loan_request.id,
                    item_id=loan_read.item.id,
                    borrower_id=loan_read.borrower.id,
                    owner_id=loan_read.item.owner_id,
                ),
            )

    return loan_reads
