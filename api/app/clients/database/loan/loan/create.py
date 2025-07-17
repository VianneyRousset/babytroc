from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.models.loan import Loan


def create_loan(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
) -> Loan:
    """Create and insert a loan."""

    # TODO add reference to loan request
    stmt = (
        insert(Loan)
        .values(
            item_id=item_id,
            borrower_id=borrower_id,
        )
        .returning(Loan)
    )

    # execute
    # TODO handle constraint violations
    loan = db.execute(stmt).unique().scalars().one()

    return loan
