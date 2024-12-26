from typing import Optional

from sqlalchemy.orm import Session

from app.clients import database
from app.enums import LoanRequestState
from app.errors.exception import LoanAlreadyInactiveError, LoanRequestStateError
from app.schemas.loan.query import LoanRequestQueryFilter
from app.schemas.loan.read import LoanRead, LoanRequestRead


def cancel_loan_request(
    db: Session,
    loan_request_id: int,
    query_filter: Optional[LoanRequestQueryFilter] = None,
    force: bool = False,
) -> LoanRequestRead:
    """Set loan request state to `canceled`.

    Loan request state must be `pending` if `force` is `False`.
    """

    # TODO generate message

    return _set_loan_request_state(
        db=db,
        loan_request_id=loan_request_id,
        state=LoanRequestState.canceled,
        query_filter=query_filter,
        force=force,
    )


def accept_loan_request(
    db: Session,
    loan_request_id: int,
    query_filter: Optional[LoanRequestQueryFilter] = None,
    force: bool = False,
) -> LoanRequestRead:
    """Set loan request state to `accepted`.

    Loan request state must be `pending` if `force` is `False`.
    """

    # TODO generate message

    return _set_loan_request_state(
        db=db,
        loan_request_id=loan_request_id,
        state=LoanRequestState.accepted,
        query_filter=query_filter,
        force=force,
    )


def reject_loan_request(
    db: Session,
    loan_request_id: int,
    query_filter: Optional[LoanRequestQueryFilter] = None,
    force: bool = False,
) -> LoanRequestRead:
    """Set loan request state to `rejected`.

    Loan request state must be `pending` if `force` is `False`.
    """

    # TODO generate message

    return _set_loan_request_state(
        db=db,
        loan_request_id=loan_request_id,
        state=LoanRequestState.rejected,
        query_filter=query_filter,
        force=force,
    )


def end_loan(
    db: Session,
    loan_id: int,
    query_filter: Optional[LoanRequestQueryFilter] = None,
):
    """Set loan end date to now.

    The loan must be active.
    """

    # TODO generate message

    # get loan from database
    loan = database.loan.get_loan(
        db=db,
        loan_id=loan_id,
        query_filter=query_filter,
    )

    # check loan state
    if loan.during.upper is not None:
        raise LoanAlreadyInactiveError()

    # set loan.during upper bound to now()
    loan = database.loan.end_loan(
        db=db,
        loan=loan,
    )

    return LoanRead.from_orm(loan)


def _set_loan_request_state(
    db: Session,
    *,
    loan_request_id: int,
    state: LoanRequestState,
    query_filter: LoanRequestQueryFilter,
    force: bool = False,
) -> LoanRequestRead:
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

    loan_request = database.loan.update_loan_request(
        db=db,
        loan_request=loan_request,
        attributes={"state": state},
    )

    return LoanRequestRead.from_orm(loan_request)
