from datetime import datetime
from typing import Annotated, Optional

from fastapi import Query, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.loan import LoanRead

from .me import router


@router.get("/loans", status_code=status.HTTP_200_OK)
def list_client_loans(
    request: Request,
    active: Annotated[
        Optional[bool],
        Query(
            title="Select only active loans",
        ),
    ] = True,
    before: Annotated[
        Optional[datetime],
        Query(
            title="Select all loans with start date before the item with this id.",
        ),
    ] = None,
    count: Annotated[
        Optional[int],
        Query(
            title="Maximum number of loans to return",
            ge=0,
        ),
    ] = None,
    db: Session = Depends(get_db_session),
) -> list[LoanRead]:
    """List loans where the client is the owner ordered by inversed start date."""

    client_user_id = services.auth.check_auth(request)

    return services.loans.list_user_loans(
        db=db,
        user_id=client_user_id,
        active=active,
        started_before_item_id=before,
        count=count,
    )
