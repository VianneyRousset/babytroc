from typing import Optional

from sqlalchemy.orm import Session, selectinload

from app.clients import database
from app.enums import LoanRequestState
from app.models.item import Item
from app.models.loan import LoanRequest
from app.schemas.loan import LoanRead, LoanRequestCreate, LoanRequestRead


async def create_loan_request(
    db: Session,
    borrower_id: int,
    loan_request: LoanRequestCreate,
):
    """Create a loan request."""

    loan_request = await database.loan.create_loan_request(
        db=db,
        borrower_id=borrower_id,
        item_id=loan_request.item_id,
        load_attributes=[LoanRequest.borrower],
        options=[
            selectinload(LoanRequest.item).selectinload(Item.images),
            selectinload(LoanRequest.item).selectinload(Item.active_loans),
        ],
    )

    return LoanRequestRead.from_orm(
        loan_request=loan_request,
        message=None,
    )


async def list_user_loan_requests(
    db: Session,
    user_id: int,
    active: Optional[bool] = None,
    created_before_loan_request_id: Optional[int] = None,
    count: Optional[int] = 64,
) -> list[LoanRequestRead]:
    """List the loan requests made by the user with `user_id`."""

    loan_requests = await database.loan.list_user_loan_requests(
        db=db,
        user_id=user_id,
        active=active,
        started_before_loan_request_id=created_before_loan_request_id,
        count=count,
    )

    return [LoanRequestRead.model_validate(req) for req in loan_requests]


async def get_loan_request_by_id(
    db: Session,
    loan_request_id: int,
    borrower_user_id: Optional[int] = None,
) -> LoanRequestRead:
    """Get loan request with ID `loan_request_id`.

    If `borrower_user_id` is given, the loan request must have this user as
    borrower.
    """

    loan_request = await database.loan.get_loan_request_by_id(
        db=db,
        loan_request_id=loan_request_id,
        borrower_user_id=borrower_user_id,
    )

    return LoanRequestRead.model_validate(loan_request)


async def cancel_loan_request(
    db: Session,
    loan_request_id: int,
    borrower_user_id: Optional[int] = None,
) -> LoanRequestRead:
    """Cancel loan request with ID `loan_request_id`.

    If `borrower_user_id` is given, the loan request must have this user as
    borrower.
    """

    loan_request = await database.loan.cancel_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        borrower_user_id=borrower_user_id,
    )

    return LoanRequestRead.model_validate(loan_request)


async def create_loan_from_loan_request(
    db: Session,
    loan_request_id: int,
    borrower_user_id: Optional[int] = None,
) -> LoanRead:
    """Create a loan from a loan request with ID `loan_request_id`.

    If `borrower_user_id` is given, the loan request must have this user as
    borrower.
    """

    loan = await database.loan.create_loan_from_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        borrower_user_id=borrower_user_id,
    )

    return LoanRead.model_validate(loan)


async def list_user_borrowings(
    db: Session,
    user_id: int,
    active: Optional[bool],
    started_before_loan_id: Optional[int],
    count: Optional[int] = 64,
) -> list[LoanRead]:
    """List the loans where the user with `user_id` is the borrower.

    If `active` is True, only return loans that are not finished.

    If started_before_item_id is not None, only return loans that started before
    the loan with this id.

    If count is provided, the number of returned loans is limited to `count`.
    """

    loans = database.list_loans(
        db=db,
        borrower_user_id=user_id,
        active=active,
        started_before_loan_id=started_before_loan_id,
        count=count,
    )

    return [LoanRead.model_validate(loan) for loan in loans]


async def list_user_item_loan_requests(
    db: Session,
    item_id: int,
    owner_user_id: Optional[int] = None,
    active: Optional[bool] = None,
    started_before_loan_request_id: Optional[int] = None,
    count: Optional[int] = None,
) -> list[LoanRequestRead]:
    """List loan reuqests made for the item with `item_id`.

    If `owner_user_id` is provided, the item must be owned by the user with this ID.

    If `active` is True, only loan requests that does not have an end date are returned.

    If `started_before_loan_request_id` is given, only loan requests that started
    before the loan request with this ID are returned.

    If `count` is given, a maximum of `count` loan reuqests are returned.
    """

    loan_requests = await database.loan.list_loan_requests(
        db=db,
        item_id=item_id,
        owner_id=owner_user_id,
        active=active,
        started_before_loan_request_id=started_before_loan_request_id,
        count=count,
    )

    loan_requests = [LoanRequestRead.model_validate(req) for req in loan_requests]

    return loan_requests


async def get_user_loan_request_by_id(
    db: Session,
    loan_request_id: int,
    item_id: Optional[int] = None,
    owner_user_id: Optional[int] = None,
) -> LoanRequestRead:
    """Get loan request with Id `loan_request_id`.

    If `item_id` is given, the item of the loan request must have this ID.

    If `owner_user_id` is given, the owner of the item of the loan request must
    have this ID.
    """

    loan_request = await database.loan.get_user_loan_request_by_id(
        db=db,
        loan_request_id=loan_request_id,
        item_id=item_id,
        owner_user_id=owner_user_id,
    )

    return LoanRequestRead.model_validate(loan_request)


async def accept_loan_request(
    db: Session,
    loan_request_id: int,
    item_id: Optional[int] = None,
    owner_user_id: Optional[int] = None,
) -> LoanRequestRead:
    """Mark loan request with `loan_request_id` as accepted.

    If `item_id` is given, the item of the loan request must have this ID.

    If `owner_user_id` is given, the owner of the item of the loan request must
    have this ID.
    """

    loan_request = await database.loan.set_loan_request_state_if_pending(
        db=db,
        loan_request_id=loan_request_id,
        item_id=item_id,
        owner_user_id=owner_user_id,
        state=LoanRequestState.accepted,
    )

    return LoanRequestRead.model_validate(loan_request)


async def reject_loan_request(
    db: Session,
    loan_request_id: int,
    item_id: Optional[int] = None,
    owner_user_id: Optional[int] = None,
) -> LoanRequestRead:
    """Mark loan request with `loan_request_id` as rejected.

    If `item_id` is given, the item of the loan request must have this ID.

    If `owner_user_id` is given, the owner of the item of the loan request must
    have this ID.
    """

    loan_request = await database.loan.set_loan_request_state_if_pending(
        db=db,
        loan_request_id=loan_request_id,
        item_id=item_id,
        owner_user_id=owner_user_id,
        state=LoanRequestState.rejected,
    )

    return LoanRequestRead.model_validate(loan_request)


async def list_user_loans(
    db: Session,
    user_id: int,
    active: Optional[bool],
    started_before_loan_id: Optional[int],
    count: Optional[int] = 64,
) -> list[LoanRead]:
    """List the loans where the user with `user_id` is the owner.

    If `active` is True, only return loans that are not finished.

    If `started_before_item_id` is given, only return loans that started before
    the loan with this id.

    If `count` is provided, the number of returned loans is limited to `count`.
    """

    loans = await database.loan.list_loans(
        db=db,
        borrower_user_id=user_id,
        active=active,
        started_before_loan_id=started_before_loan_id,
        count=count,
    )

    return [LoanRead.model_validate(loan) for loan in loans]
