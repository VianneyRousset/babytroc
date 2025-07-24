from typing import Annotated

from fastapi import Depends, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.loan.query import LoanRequestQueryFilter
from app.schemas.loan.read import LoanRequestRead

from .annotations import loan_request_id_annotation
from .router import router


@router.post("/{loan_request_id}/accept", status_code=status.HTTP_200_OK)
def accept_client_item_loan_request(
    client_id: client_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRequestRead:
    """Accept loan request where the client is the owner."""

    return services.loan.accept_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestQueryFilter(
            owner_id=client_id,
        ),
    )


@router.post("/{loan_request_id}/reject", status_code=status.HTTP_200_OK)
def reject_client_item_loan_request(
    client_id: client_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRequestRead:
    """Reject loan request where the client is the owner."""

    return services.loan.reject_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestQueryFilter(
            owner_id=client_id,
        ),
    )
