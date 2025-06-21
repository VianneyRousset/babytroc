from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.chat.base import ChatId
from app.schemas.loan.read import LoanRequestRead
from app.services.chat import send_message_loan_request_created


def create_loan_request(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
) -> LoanRequestRead:
    """Create a loan request."""

    loan_request = database.loan.create_loan_request(
        db=db,
        borrower_id=borrower_id,
        item_id=item_id,
    )

    # create messages
    send_message_loan_request_created(
        db=db,
        chat_id=ChatId.from_values(
            item_id=item_id,
            borrower_id=borrower_id,
        ),
        loan_request_id=loan_request.id,
    )

    return LoanRequestRead.model_validate(loan_request)
