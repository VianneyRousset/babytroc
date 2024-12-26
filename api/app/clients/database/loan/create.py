from collections.abc import Collection
from typing import Optional

from sqlalchemy.orm import Session

from app.clients.database import dbutils
from app.clients.database.item import get_item
from app.clients.database.user import get_user
from app.models.item import Item
from app.models.loan import Loan, LoanRequest

from .read import get_loan_request


def create_loan_request(
    db: Session,
    *,
    borrower_id: int,
    item_id: int,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> LoanRequest:
    """Create and insert a loan request."""

    loan_request = LoanRequest()

    loan_request.borrower = get_user(
        db=db,
        user_id=borrower_id,
    )

    return insert_loan_request(
        db=db,
        loan_request=loan_request,
        item_id=item_id,
        load_attributes=load_attributes,
        options=options,
    )


def insert_loan_request(
    db: Session,
    *,
    loan_request: LoanRequest,
    item_id: int,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> LoanRequest:
    """Insert `loan_request` into the loan request of the item with `item_id`."""

    item = get_item(db, item_id, load_attributes=[Item.loan_requests])
    item.loan_requests.append(loan_request)

    db.flush()
    db.refresh(loan_request)

    return get_loan_request(
        db=db,
        loan_request_id=loan_request.id,
        load_attributes=load_attributes,
        options=options,
    )


def create_loan(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> Loan:
    """Create and insert a loan."""

    loan = Loan()

    loan.borrower = get_user(db=db, user_id=borrower_id)

    return insert_loan(
        db=db,
        loan=loan,
        item_id=item_id,
        load_attributes=load_attributes,
        options=options,
    )


def insert_loan(
    db: Session,
    *,
    loan: Loan,
    item_id: int,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> Loan:
    """Insert `loan` into the loans of the item with `item_id`."""

    item = get_item(db, item_id, load_attributes=[Item.loans])

    item.loan.append(loan)

    db.flush()
    db.refresh(loan)

    return get_loan_request(
        db=db,
        loan_id=loan.id,
        load_attributes=load_attributes,
        options=options,
    )
