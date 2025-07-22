from typing import Annotated

from fastapi import Depends, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.loan.query import LoanQueryFilter
from app.schemas.loan.read import LoanRead

from .annotations import loan_id_annotation
from .router import router


@router.post("/{loan_id}/end", status_code=status.HTTP_200_OK)
def end_client_loan(
    client_id: client_id_annotation,
    loan_id: loan_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRead:
    """End the loan where the client is the owner."""

    return services.loan.end_loan(
        db=db,
        loan_id=loan_id,
        query_filter=LoanQueryFilter(
            owner_id=client_id,
        ),
    )
