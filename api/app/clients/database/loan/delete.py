from sqlalchemy.orm import Session

from app.models.loan import LoanRequest


def delete_loan_request(
    db: Session,
    loan_request: LoanRequest,
) -> None:
    """Delete the given `loan_request`."""

    db.delete(loan_request)
    db.flush()
