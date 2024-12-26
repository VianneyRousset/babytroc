from typing import Optional

from sqlalchemy.orm import Session

from .read import get_loan_request


def delete_loan_request(
    db: Session,
    loan_request_id: int,
    *,
    item_id: Optional[int] = None,
    borrower_id: Optional[int] = None,
    owner_id: Optional[int] = None,
) -> None:
    """Delete the loan request with ID `loan_request_id`.

    If `item_id` is provided, the requested item must have the latter ID.
    If `borrower_id` is provided, the borrower must have the latter user ID.
    If `owner_id` is provided, the owner must have the latter user ID.
    """

    loan_request = get_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        item_id=item_id,
        borrower_id=borrower_id,
        owner_id=owner_id,
    )

    db.delete(loan_request)
    db.flush()
