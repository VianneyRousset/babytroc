from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.clients.database.item import get_item
from app.clients.database.user import get_user
from app.errors.loan import LoanRequestAlreadyExistsError, LoanRequestOwnItemError
from app.models.loan import Loan, LoanRequest


def create_loan_request(
    db: Session,
    *,
    borrower_id: int,
    item_id: int,
) -> LoanRequest:
    """Create and insert a loan request."""

    loan_request = LoanRequest(
        borrower_id=borrower_id,
        item_id=item_id,
    )

    return insert_loan_request(
        db=db,
        loan_request=loan_request,
    )


def insert_loan_request(
    db: Session,
    *,
    loan_request: LoanRequest,
) -> LoanRequest:
    """Insert `loan_request` into the loan request of the item with `item_id`."""

    # check borrower exists
    get_user(db=db, user_id=loan_request.borrower_id)

    # check item exists
    item = get_item(db=db, item_id=loan_request.item_id)

    # check item is not owned by borrower
    if item.owner_id == loan_request.borrower_id:
        raise LoanRequestOwnItemError()

    db.add(loan_request)

    try:
        db.flush()

    except IntegrityError as error:
        raise LoanRequestAlreadyExistsError() from error

    db.refresh(loan_request)

    return loan_request


def create_loan(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
) -> Loan:
    """Create and insert a loan."""

    borrower = get_user(db=db, user_id=borrower_id)
    item = get_item(db=db, item_id=item_id)

    loan = Loan()
    db.add(loan)

    loan.borrower = borrower
    loan.item = item

    db.flush()
    db.refresh(loan)

    return loan
