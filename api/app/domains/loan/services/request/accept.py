from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.loan.enums import LoanRequestState
from app.domains.loan.events import LoanRequestAccepted
from app.domains.loan.schemas.query import LoanRequestUpdateQueryFilter
from app.domains.loan.schemas.read import LoanRequestRead
from app.infrastructure.events import emit

from .update import update_many_loan_requests_state


async def accept_loan_request(
    db: AsyncSession,
    loan_request_id: int,
    query_filter: LoanRequestUpdateQueryFilter | None = None,
    check_state: bool = True,
) -> LoanRequestRead:
    """Set loan request state to `accepted`.

    Loan request state must be `pending` or `rejected` if `check_state` is `True`
    (default).
    """

    loan_requests = await accept_many_loan_requests(
        db=db,
        loan_request_ids={loan_request_id},
        query_filter=query_filter,
        check_state=check_state,
    )

    return loan_requests[0]


async def accept_many_loan_requests(
    db: AsyncSession,
    loan_request_ids: set[int],
    query_filter: LoanRequestUpdateQueryFilter | None = None,
    check_state: bool = True,
    send_messages: bool = True,
) -> list[LoanRequestRead]:
    """Set state of given loan requests to `acceptled`.

    All loan request state must be `pending` or `rejected` if `check_state` is `True`
    (default).
    """

    query_filter = query_filter or LoanRequestUpdateQueryFilter()

    # ensure proper state of the updated loan request
    if check_state:
        query_filter.states = (query_filter.states or set()) | {
            LoanRequestState.pending,
            LoanRequestState.rejected,
        }

    # update state
    loan_requests = await update_many_loan_requests_state(
        db=db,
        loan_request_ids=loan_request_ids,
        state=LoanRequestState.accepted,
        query_filter=query_filter,
    )

    # emit events
    if send_messages:
        for lr in loan_requests:
            await emit(
                db,
                LoanRequestAccepted(
                    loan_request_id=lr.id,
                    item_id=lr.item.id,
                    borrower_id=lr.borrower.id,
                    owner_id=lr.item.owner_id,
                ),
            )

    return loan_requests
