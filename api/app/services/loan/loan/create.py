from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import LoanRequestState
from app.models.loan import Loan, LoanRequest
from app.schemas.chat.base import ChatId
from app.schemas.chat.send import SendChatMessageLoanStarted
from app.schemas.loan.query import LoanRequestUpdateQueryFilter
from app.schemas.loan.read import LoanRead
from app.services.chat import send_many_chat_messages
from app.services.loan.request.update import update_many_loan_requests_state


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
    loan_requests = await update_many_loan_requests_state(
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
            [Loan.item_id, Loan.borrower_id, Loan.loan_request_id],
            select(LoanRequest.item_id, LoanRequest.borrower_id, LoanRequest.id).where(
                LoanRequest.id.in_(loan_request_ids)
            ),
        )
        .returning(Loan)
    )

    loans = (await db.execute(create_loans_stmt)).unique().scalars().all()

    # check the number of created loans matched the number of given loan requests
    if len(loans) != len(loan_request_ids):
        msg = (
            "The number of created loans does not match the number of given "
            "loan request ids. The reason is unexpected."
        )
        raise RuntimeError(msg)

    # create messages
    if send_messages:
        await send_many_chat_messages(
            db=db,
            messages=[
                SendChatMessageLoanStarted(
                    chat_id=ChatId.from_values(
                        item_id=loan_request.item.id,
                        borrower_id=loan_request.borrower.id,
                    ),
                    loan_id=loan.id,
                )
                for loan_request, loan in zip(loan_requests, loans, strict=True)
            ],
        )

    return [LoanRead.model_validate(loan) for loan in loans]
