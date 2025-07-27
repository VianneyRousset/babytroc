from sqlalchemy.orm import Session

from app.clients import database
from app.errors.loan import LoanAlreadyInactiveError
from app.schemas.chat.base import ChatId
from app.schemas.loan.query import LoanReadQueryFilter
from app.schemas.loan.read import LoanRead
from app.services.chat import send_message_loan_ended


def end_loan(
    db: Session,
    loan_id: int,
    query_filter: LoanReadQueryFilter | None = None,
):
    """Set loan end date to now.

    The loan must be active.
    """

    # get loan from database
    loan = database.loan.get_loan(
        db=db,
        loan_id=loan_id,
        query_filter=query_filter,
    )

    # check loan state
    if loan.during.upper is not None:
        raise LoanAlreadyInactiveError()

    # create chat message
    send_message_loan_ended(
        db=db,
        chat_id=ChatId.from_values(
            item_id=loan.item_id,
            borrower_id=loan.borrower_id,
        ),
        loan_id=loan.id,
    )

    # set loan.during upper bound to now()
    loan = database.loan.end_loan(
        db=db,
        loan=loan,
    )

    return LoanRead.model_validate(loan)
