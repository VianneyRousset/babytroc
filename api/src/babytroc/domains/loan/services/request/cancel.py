from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.loan.enums import LoanRequestState
from babytroc.domains.loan.errors import LoanRequestNotFoundError, LoanRequestStateError
from babytroc.domains.loan.events import LoanRequestCancelled
from babytroc.domains.loan.models import LoanRequest
from babytroc.domains.loan.schemas.query import (
    LoanRequestQueryPageCursor,
    LoanRequestReadQueryFilter,
    LoanRequestUpdateQueryFilter,
)
from babytroc.domains.loan.schemas.read import LoanRequestRead
from babytroc.infrastructure.events import emit
from babytroc.shared.pagination import QueryPageOptions

from .read import get_loan_request, list_loan_requests
from .update import update_many_loan_requests_state


async def cancel_item_active_loan_request(
    db: AsyncSession,
    *,
    item_id: int,
    borrower_id: int,
    send_message: bool = True,
) -> LoanRequestRead:
    """Cancel the active loan request made by `borrower_id` to `item_id`.

    An active loan request is defined as being in 'pending' or 'accepted' state.
    """

    # update all loan requests states to executed
    stmt = (
        update(LoanRequest)
        .values(state=LoanRequestState.cancelled)
        .where(LoanRequest.item_id == item_id)
        .where(LoanRequest.borrower_id == borrower_id)
        .where(LoanRequest.state.in_(LoanRequestState.get_active_states()))
    ).returning(LoanRequest)

    try:
        loan_request = (await db.execute(stmt)).unique().scalars().one()

    # if no loan request matches, it means either:
    # 1. No loan request with the given `item_id` and `borrower_id` exists
    # 2. the loan request exists but is inactive
    except NoResultFound as error:
        # raise LoanRequestNotFound if loan request does not exist (1.)
        result = await list_loan_requests(
            db=db,
            query_filter=LoanRequestReadQueryFilter(
                item_id=item_id,
                borrower_id=borrower_id,
            ),
            page_options=QueryPageOptions(
                limit=1,
                cursor=LoanRequestQueryPageCursor(),
            ),
        )

        if not result.data:
            raise LoanRequestNotFoundError(
                {"item_id": item_id, "borrower_id": borrower_id}
            ) from error

        loan_request_causing_issue = result.data[0]

        # raise LoanRequestStateError if the loan request is inactive
        raise LoanRequestStateError(
            expected_state=LoanRequestState.get_active_states(),
            actual_state=loan_request_causing_issue.state,
        ) from error

    loan_request_read = await get_loan_request(
        db=db,
        loan_request_id=loan_request.id,
    )

    # emit event
    if send_message:
        await emit(
            db,
            LoanRequestCancelled(
                loan_request_id=loan_request_read.id,
                item_id=loan_request_read.item.id,
                borrower_id=loan_request_read.borrower.id,
                owner_id=loan_request_read.item.owner_id,
            ),
        )

    return loan_request_read


async def cancel_loan_request(
    db: AsyncSession,
    loan_request_id: int,
    *,
    query_filter: LoanRequestUpdateQueryFilter | None = None,
    check_state: bool = True,
    send_message: bool = True,
) -> LoanRequestRead:
    """Set loan request state to `cancelled`.

    Loan request state must be `pending` if `check_state` is `True` (default).
    """

    loan_requests = await cancel_many_loan_requests(
        db=db,
        loan_request_ids={loan_request_id},
        query_filter=query_filter,
        check_state=check_state,
        send_messages=send_message,
    )

    return loan_requests[0]


async def cancel_many_loan_requests(
    db: AsyncSession,
    loan_request_ids: set[int],
    query_filter: LoanRequestUpdateQueryFilter | None = None,
    check_state: bool = True,
    send_messages: bool = True,
) -> list[LoanRequestRead]:
    """Set state of given loan requests to `cancelled`.

    All loan request state must be `pending` if `check_state` is `True` (default).
    """

    query_filter = query_filter or LoanRequestUpdateQueryFilter()

    # ensure proper state of the updated loan request
    if check_state:
        query_filter.states = (query_filter.states or set()) | {
            LoanRequestState.pending,
        }

    # update state
    loan_requests = await update_many_loan_requests_state(
        db=db,
        loan_request_ids=loan_request_ids,
        state=LoanRequestState.cancelled,
        query_filter=query_filter,
    )

    # emit events
    if send_messages:
        for lr in loan_requests:
            await emit(
                db,
                LoanRequestCancelled(
                    loan_request_id=lr.id,
                    item_id=lr.item.id,
                    borrower_id=lr.borrower.id,
                    owner_id=lr.item.owner_id,
                ),
            )

    return loan_requests
