from sqlalchemy import update
from sqlalchemy.orm import Session

from app.enums import LoanRequestState
from app.errors.loan import LoanRequestStateError
from app.models.loan import LoanRequest
from app.schemas.loan.query import (
    LoanRequestReadQueryFilter,
    LoanRequestUpdateQueryFilter,
)
from app.schemas.loan.read import LoanRequestRead
from app.services.loan.request.read import get_loan_request


def update_loan_request_state(
    db: Session,
    loan_request_id: int,
    state: LoanRequestState,
    *,
    query_filter: LoanRequestUpdateQueryFilter | None = None,
) -> LoanRequestRead:
    """Set the state of given loan requests.

    Errors are raised if any of the given loan requests does not match the
    given query_filter.
    """

    loan_requests = update_many_loan_requests_state(
        db=db,
        loan_request_ids={loan_request_id},
        state=state,
        query_filter=query_filter,
    )

    return loan_requests[0]


def update_many_loan_requests_state(
    db: Session,
    loan_request_ids: set[int],
    state: LoanRequestState,
    *,
    query_filter: LoanRequestUpdateQueryFilter | None = None,
) -> list[LoanRequestRead]:
    """Set the state of given loan requests.

    Errors are raised if any of the given loan requests does not match the
    given query_filter.
    """

    query_filter = query_filter or LoanRequestUpdateQueryFilter()

    # update all loan requests states to executed
    stmt = query_filter.filter_update(
        update(LoanRequest)
        .values(state=state)
        .where(LoanRequest.id.in_(loan_request_ids))
    ).returning(LoanRequest)

    loan_requests = db.execute(stmt).unique().scalars().all()

    # if not all given loan requests were updated it means either:
    # 1. the given loan request matching the query_filter does not exist
    # 2. the given loan request state is wrong
    if len(loan_requests) != len(loan_request_ids):
        # find missing loan request ids
        missing_loan_request_ids = loan_request_ids - {req.id for req in loan_requests}
        first_missing_loan_request_id = next(iter(sorted(missing_loan_request_ids)))

        # raise LoanRequestNotFoundError if loan request does not exist (1.)
        loan_request = get_loan_request(
            db=db,
            loan_request_id=first_missing_loan_request_id,
            query_filter=LoanRequestReadQueryFilter.model_validate(
                {**query_filter.model_dump(exclude={"states"})}
            ),
        )

        # raise LoanRequestStateError if loan request state is wrong (2.)
        if (
            query_filter.states is not None
            and loan_request.state not in query_filter.states
        ):
            raise LoanRequestStateError(
                expected_state=query_filter.states,
                actual_state=loan_request.state,
            )

        msg = (
            "The number of updated loan requests does not match the number of given "
            "loan request ids. The reason is unexpected."
        )
        raise RuntimeError(msg)

    return [LoanRequestRead.model_validate(req) for req in loan_requests]
