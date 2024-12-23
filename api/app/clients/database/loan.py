from collections.abc import Collection
from typing import Any, Mapping, Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.clients.database import dbutils
from app.clients.database.item import get_item
from app.clients.database.user import get_user
from app.errors.exception import LoanNotFoundError, LoanRequestNotFoundError
from app.models.item import Item
from app.models.loan import Loan, LoanRequest


async def create_loan_request(
    db: Session,
    *,
    borrower_id: int,
    item_id: int,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
):
    """Create and insert a loan request."""

    loan_request = LoanRequest()

    loan_request.borrower = await get_user(
        db=db,
        user_id=borrower_id,
    )

    return await insert_loan_request(
        db=db,
        loan_request=loan_request,
        item_id=item_id,
        load_attributes=load_attributes,
        options=options,
    )


async def insert_loan_request(
    db: Session,
    *,
    loan_request: LoanRequest,
    item_id: int,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> LoanRequest:
    """Insert loan request into the database."""

    item = await get_item(db, item_id, load_attributes=[Item.loan_requests])
    item.loan_requests.append(loan_request)

    await db.flush()
    await db.refresh(loan_request)

    return await get_loan_request(
        db=db,
        loan_request_id=loan_request.id,
        load_attributes=load_attributes,
        options=options,
    )


async def get_loan_request(
    db: Session,
    loan_request_id: int,
    item_id: Optional[int] = None,
    borrower_id: Optional[int] = None,
    *,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
):
    """Get loan request with ID `loan_request_id`.

    If `item_id` is provided, the requested item must have the latter ID.

    If `borrower_id` is provided, the borrower must have the latter ID.
    """

    stmt = select(LoanRequest).where(LoanRequest.id == loan_request_id)

    if item_id is not None:
        stmt = stmt.where(LoanRequest.id == loan_request_id)

    if borrower_id is not None:
        stmt = stmt.where(LoanRequest.borrower_id == loan_request_id)

    stmt = dbutils.add_default_query_options(
        stmt=stmt,
        load_attributes=load_attributes,
        options=options,
    )

    try:
        return (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        key = {
            "loan_request_id": loan_request_id,
            "item_id": item_id,
            "borrower_id": borrower_id,
        }
        key = {k: v for k, v in key.items() if v is not None}
        raise LoanRequestNotFoundError(key) from error


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
