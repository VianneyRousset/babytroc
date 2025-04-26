from sqlalchemy.orm import Session

from app.clients import database
from app.enums import LoanRequestState
from app.errors.loan import LoanAlreadyInactiveError, LoanRequestStateError
from app.schemas.chat.base import ChatId
from app.schemas.loan.query import LoanQueryFilter, LoanRequestQueryFilter
from app.schemas.loan.read import LoanRead, LoanRequestRead
from app.services.chat import (
    send_message_loan_ended,
    send_message_loan_request_accepted,
    send_message_loan_request_cancelled,
    send_message_loan_request_rejected,
)


def cancel_active_loan_request(
    db: Session,
    *,
    item_id: int,
    borrower_id: int,
) -> LoanRequestRead:
    """Cancel the active loan request made by `borrower_id` to `item_id`.

    An active loan request is defined as being in 'pending' or 'accepted' state.
    """

    # find pending loan request
    loan_request = database.loan.get_loan_request(
        db=db,
        query_filter=LoanRequestQueryFilter(
            item_id=item_id,
            borrower_id=borrower_id,
            states={LoanRequestState.pending, LoanRequestState.accepted},
        ),
    )

    return cancel_loan_request(
        db=db,
        loan_request_id=loan_request.id,
    )


def cancel_loan_request(
    db: Session,
    loan_request_id: int,
    query_filter: LoanRequestQueryFilter | None = None,
    force: bool = False,
) -> LoanRequestRead:
    """Set loan request state to `cancelled`.

    Loan request state must be `pending` if `force` is `False`.
    """

    # get loan request from database
    loan_request = database.loan.get_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=query_filter,
    )

    # check loan request state
    active_states = {LoanRequestState.pending, LoanRequestState.accepted}
    if not force and loan_request.state not in active_states:
        raise LoanRequestStateError(
            expected_state=active_states,
            actual_state=loan_request.state,
        )

    # update loan request state
    loan_request = database.loan.update_loan_request(
        db=db,
        loan_request=loan_request,
        attributes={"state": LoanRequestState.cancelled},
    )

    # create chat message
    send_message_loan_request_cancelled(
        db=db,
        chat_id=ChatId(
            item_id=loan_request.item_id,
            borrower_id=loan_request.borrower_id,
        ),
        loan_request_id=loan_request.id,
    )

    return LoanRequestRead.model_validate(loan_request)


def accept_loan_request(
    db: Session,
    loan_request_id: int,
    query_filter: LoanRequestQueryFilter | None = None,
    force: bool = False,
) -> LoanRequestRead:
    """Set loan request state to `accepted`.

    Loan request state must be `pending` if `force` is `False`.
    """

    # get loan request from database
    loan_request = database.loan.get_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=query_filter,
    )

    # check loan request state
    if not force and loan_request.state != LoanRequestState.pending:
        raise LoanRequestStateError(
            expected_state=LoanRequestState.pending,
            actual_state=loan_request.state,
        )

    # update loan request state
    loan_request = database.loan.update_loan_request(
        db=db,
        loan_request=loan_request,
        attributes={"state": LoanRequestState.accepted},
    )

    # create chat message
    send_message_loan_request_accepted(
        db=db,
        chat_id=ChatId(
            item_id=loan_request.item_id,
            borrower_id=loan_request.borrower_id,
        ),
        loan_request_id=loan_request.id,
    )

    return LoanRequestRead.model_validate(loan_request)


def reject_loan_request(
    db: Session,
    loan_request_id: int,
    query_filter: LoanRequestQueryFilter | None = None,
    force: bool = False,
) -> LoanRequestRead:
    """Set loan request state to `rejected`.

    Loan request state must be `pending` if `force` is `False`.
    """

    # get loan request from database
    loan_request = database.loan.get_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=query_filter,
    )

    # check loan request state
    active_states = {
        LoanRequestState.pending,
        LoanRequestState.accepted,
    }
    if not force and loan_request.state not in active_states:
        raise LoanRequestStateError(
            expected_state=active_states,
            actual_state=loan_request.state,
        )

    # update loan request state
    loan_request = database.loan.update_loan_request(
        db=db,
        loan_request=loan_request,
        attributes={"state": LoanRequestState.rejected},
    )

    # create chat message
    send_message_loan_request_rejected(
        db=db,
        chat_id=ChatId(
            item_id=loan_request.item_id,
            borrower_id=loan_request.borrower_id,
        ),
        loan_request_id=loan_request.id,
    )

    return LoanRequestRead.model_validate(loan_request)


def end_loan(
    db: Session,
    loan_id: int,
    query_filter: LoanQueryFilter | None = None,
):
    """Set loan end date to now.

    The loan must be active.
    """

    # get loan from database
    loan = database.loan.get_loan(
        db=db,
        loan_id=loan_id,
        query_filter=query_filter,
    )

    # check loan state
    if loan.during.upper is not None:
        raise LoanAlreadyInactiveError()

    # create chat message
    send_message_loan_ended(
        db=db,
        chat_id=ChatId(
            item_id=loan.item_id,
            borrower_id=loan.borrower_id,
        ),
        loan_id=loan.id,
    )

    # set loan.during upper bound to now()
    loan = database.loan.end_loan(
        db=db,
        loan=loan,
    )

    return LoanRead.model_validate(loan)
