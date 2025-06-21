from sqlalchemy.orm import Session

from app.clients.database.item import get_item
from app.clients.database.user import get_user
from app.models.loan import Loan


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
