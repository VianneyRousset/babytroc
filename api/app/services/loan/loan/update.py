from sqlalchemy import text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.loan import LoanAlreadyInactiveError
from app.models.loan import Loan
from app.schemas.chat.base import ChatId
from app.schemas.chat.send import SendChatMessageLoanEnded
from app.schemas.loan.query import LoanReadQueryFilter, LoanUpdateQueryFilter
from app.schemas.loan.read import LoanRead
from app.services.chat import send_many_chat_messages

from .read import get_many_loans


async def end_loan(
    db: AsyncSession,
    loan_id: int,
    *,
    query_filter: LoanUpdateQueryFilter | None = None,
    send_message: bool = True,
) -> LoanRead:
    """Set loan end date to now.
    The loan must be active.
    """

    loans = await end_many_loans(
        db=db,
        loan_ids={loan_id},
        query_filter=query_filter,
        send_messages=send_message,
    )

    return loans[0]


async def end_many_loans(
    db: AsyncSession,
    loan_ids: set[int],
    *,
    query_filter: LoanUpdateQueryFilter | None = None,
    send_messages: bool = True,
) -> list[LoanRead]:
    """Set many loan end date to now.
    The loans must be active.
    """

    query_filter = query_filter or LoanUpdateQueryFilter()

    stmt = query_filter.filter_update(
        update(Loan)
        .values(during=Loan.during * text("tstzrange(NULL, now(), '()')"))
        .where(Loan.id.in_(loan_ids))
    ).returning(Loan.id)

    res = await db.execute(stmt)
    updated_loan_ids = set(res.unique().scalars().all())

    # if not all given loans were updated it means either:
    # 1. the given loan matching the query_filter does not exist
    # 2. the given loan were not active (non-null upper bound of range `during`)
    if len(updated_loan_ids) != len(loan_ids):
        # find missing loan request ids
        missing_loan_ids = loan_ids - updated_loan_ids

        # raise LoanNotFoundError if loan request does not exist (1.)
        loans = await get_many_loans(
            db=db,
            loan_ids=missing_loan_ids,
            query_filter=LoanReadQueryFilter.model_validate(query_filter.model_dump()),
        )

        # raise LoanAlreadyInactiveError if the loan were already inactive (2.)
        if inactive_loan_ids := {
            loan.id for loan in loans if loan.during[1] is not None
        }:
            raise LoanAlreadyInactiveError(inactive_loan_ids)

        msg = (
            "The number of updated loans does not match the number of given "
            "loan ids. The reason is unexpected."
        )
        raise RuntimeError(msg)

    loans = await get_many_loans(
        db=db,
        loan_ids=loan_ids,
    )

    # create chat message
    if send_messages:
        await send_many_chat_messages(
            db=db,
            messages=[
                SendChatMessageLoanEnded(
                    chat_id=ChatId.from_values(
                        item_id=loan.item.id,
                        borrower_id=loan.borrower.id,
                    ),
                    loan_id=loan.id,
                )
                for loan in loans
            ],
        )

    return loans
