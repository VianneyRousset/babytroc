from typing import Annotated

from fastapi import Depends, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.loan.query import LoanRequestReadQueryFilter
from app.schemas.loan.read import LoanRead, LoanRequestRead

from .annotations import loan_request_id_annotation
from .router import router


@router.post("/{loan_request_id}/cancel", status_code=status.HTTP_201_CREATED)
def cancel_borrowing_loan_request(
    client_id: client_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRequestRead:
    """Cancel pending loan request where the client is the borrower."""

    return services.loan.cancel_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestReadQueryFilter(
            borrower_id=client_id,
        ),
    )


@router.post("/{loan_request_id}/execute", status_code=status.HTTP_201_CREATED)
def execute_loan_request(
    client_id: client_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRead:
    """Create a loan from an accepted loan request."""

    # get list of loan requests of the item
    return services.loan.execute_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestReadQueryFilter(
            borrower_id=client_id,
        ),
    )
