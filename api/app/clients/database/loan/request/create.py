from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors.loan import LoanRequestAlreadyExistsError
from app.models.loan import LoanRequest


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

    # check item is not owned by borrower
    # TODO put back check item exists and is not owned by borrower

    db.add(loan_request)

    try:
        db.flush()

    # TODO get item and user to find which is missing
    except IntegrityError as error:
        raise LoanRequestAlreadyExistsError() from error

    db.refresh(loan_request)

    return loan_request
