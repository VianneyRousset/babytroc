from typing import Optional

from sqlalchemy.orm import Session

from app.clients import database
from app.enums import LoanRequestState
from app.errors.exception import LoanRequestStateError
from app.schemas.loan.query import LoanRequestQueryFilter
from app.schemas.loan.read import LoanRequestRead


def cancel_loan_request(
    db: Session,
    loan_request_id: int,
    query_filter: Optional[LoanRequestQueryFilter] = None,
    force: Optional[bool] = False,
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
    force: Optional[bool] = False,
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
    force: Optional[bool] = False,
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


def _set_loan_request_state(
    db: Session,
    *,
    loan_request_id: int,
    state: LoanRequestState,
    query_filter: LoanRequestQueryFilter,
    force: Optional[bool] = False,
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
