from sqlalchemy.orm import Session

from app.clients.database.item import get_item
from app.clients.database.user import get_user
from app.models.loan import Loan, LoanRequest


def create_loan_request(
    db: Session,
    *,
    borrower_id: int,
    item_id: int,
    creation_chat_message_id: int,
) -> LoanRequest:
    """Create and insert a loan request."""

    loan_request = LoanRequest(
        creation_chat_message_id=creation_chat_message_id,
    )

    loan_request.borrower = get_user(
        db=db,
        user_id=borrower_id,
    )

    return insert_loan_request(
        db=db,
        loan_request=loan_request,
        item_id=item_id,
    )


def insert_loan_request(
    db: Session,
    *,
    loan_request: LoanRequest,
    item_id: int,
) -> LoanRequest:
    """Insert `loan_request` into the loan request of the item with `item_id`."""

    item = get_item(
        db=db,
        item_id=item_id,
    )
    item.loan_requests.append(loan_request)

    db.flush()
    db.refresh(loan_request)

    return loan_request


def create_loan(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
    creation_chat_message_id: int,
) -> Loan:
    """Create and insert a loan."""

    loan = Loan(
        creation_chat_message_id=creation_chat_message_id,
    )

    loan.borrower = get_user(db=db, user_id=borrower_id)

    return insert_loan(
        db=db,
        loan=loan,
        item_id=item_id,
    )


def insert_loan(
    db: Session,
    *,
    loan: Loan,
    item_id: int,
) -> Loan:
    """Insert `loan` into the loans of the item with `item_id`."""

    item = get_item(
        db=db,
        item_id=item_id,
    )

    item.loans.append(loan)

    db.flush()
    db.refresh(loan)

    return loan
