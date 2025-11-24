from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import LoanRequestState
from app.schemas.chat.base import ChatId
from app.schemas.chat.send import SendChatMessageLoanRequestAccepted
from app.schemas.loan.query import LoanRequestUpdateQueryFilter
from app.schemas.loan.read import LoanRequestRead
from app.services.chat import send_many_chat_messages

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

    query_filter = LoanRequestUpdateQueryFilter()

    # ensure proper state of the updated loan request
    if check_state:
        query_filter.states = (query_filter.states or set()) | {
            LoanRequestState.pending,
        }

    # update state
    loan_requests = await update_many_loan_requests_state(
        db=db,
        loan_request_ids=loan_request_ids,
        state=LoanRequestState.accepted,
        query_filter=query_filter,
    )

    # create chat message
    if send_messages:
        await send_many_chat_messages(
            db=db,
            messages=[
                SendChatMessageLoanRequestAccepted(
                    chat_id=ChatId.from_values(
                        item_id=loan_request.item.id,
                        borrower_id=loan_request.borrower.id,
                    ),
                    loan_request_id=loan_request.id,
                )
                for loan_request in loan_requests
            ],
        )

    return loan_requests
