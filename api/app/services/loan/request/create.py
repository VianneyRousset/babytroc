from sqlalchemy import insert, literal, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from app.errors.loan import LoanRequestAlreadyExistsError, LoanRequestOwnItemError
from app.models.item import Item
from app.models.loan import LoanRequest
from app.schemas.chat.base import ChatId
from app.schemas.loan.read import LoanRequestRead
from app.services.chat import send_message_loan_request_created


def create_loan_request(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
) -> LoanRequestRead:
    """Create a loan request."""

    # insert loan request while preventing the borrower to be the owner of the object
    # (implemented using from_select where the source item owner must be different
    # than the borrower)
    stmt = (
        insert(LoanRequest)
        .from_select(
            [LoanRequest.item_id, LoanRequest.borrower_id],
            select(Item.id, literal(borrower_id))
            .where(Item.id == item_id)
            .where(Item.owner_id != borrower_id),
        )
        .returning(LoanRequest)
    )

    # execute
    try:
        loan_request = db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        raise LoanRequestOwnItemError() from error

    except IntegrityError as error:
        raise LoanRequestAlreadyExistsError() from error

    # create messages
    send_message_loan_request_created(
        db=db,
        chat_id=ChatId.from_values(
            item_id=item_id,
            borrower_id=borrower_id,
        ),
        loan_request_id=loan_request.id,
    )

    return LoanRequestRead.model_validate(loan_request)
