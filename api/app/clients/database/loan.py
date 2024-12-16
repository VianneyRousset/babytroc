from typing import Any, Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors.exception import LoanNotFoundError, LoanRequestNotFoundError
from app.models.loan import Loan, LoanRequest


async def insert_loan_request(
    db: Session,
    loan_request: LoanRequest,
) -> LoanRequest:
    """
    Create a loan request from the owner with `owner_id` to the item with `item_id`.

    Returns
    -------
    loan_request: LoanRequest
        The created loan request.
    """

    db.add(loan_request)
    await db.flush()
    await db.refresh(loan_request)

    return loan_request


async def delete_loan_request(db: Session, item_id: int, owner_id: int) -> None:
    """Delete the loan request from database."""

    key = {
        "item_id": item_id,
        "owner_id": owner_id,
    }

    loan_request = await db.get(LoanRequest, key)

    if not loan_request:
        raise LoanRequestNotFoundError(key)

    await db.delete(loan_request)
    await db.flush()
    await db.refresh(loan_request)


async def insert_loan(db: Session, loan: Loan) -> Loan:
    """
    Create a loan.

    Returns
    -------
        The created loan.
    """

    db.add(loan)
    await db.flush()
    await db.refresh(loan)

    return loan


async def get_owner_loans(db: Session, owner_id: int) -> list[Loan]:
    """
    Get all loans where the item is owner by `owner_id`.

    Returns
    -------
    loans: list[Loan]
        List of loans.
    """

    return await select(Loan).where(Loan.item.owner_id == owner_id).all()


async def update_loan(
    db: Session,
    loan_id: int,
    **attributes: Mapping[str, Any],
) -> Loan:
    """
    Update the given `attributes` of the loan with `loan_id`.

    Returns
    -------
    loan: Loan
        The updated loan.
    """

    loan = await db.get(Loan, loan_id)

    if not loan:
        raise LoanNotFoundError({"loan_id": loan_id})

    for key, value in attributes.items():
        setattr(loan, key, value)

    await db.flush()
    await db.refresh(loan)

    return loan
