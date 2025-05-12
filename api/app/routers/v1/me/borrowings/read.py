from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.loan.api import LoanApiQuery
from app.schemas.loan.query import LoanQueryFilter
from app.schemas.loan.read import LoanRead
from app.schemas.query import QueryPageOptions

from .router import router

# READ


@router.get("", status_code=status.HTTP_200_OK)
def list_client_borrowings(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    query: Annotated[LoanApiQuery, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[LoanRead]:
    """List loans where the client is the borrower."""

    result = services.loan.list_loans(
        db=db,
        query_filter=LoanQueryFilter(
            borrower_id=client_id,
            item_id=query.item,
            active=query.active,
        ),
        page_options=QueryPageOptions(
            order=["loan_id"],
            desc=True,
        ),
    )

    response.headers["X-Total-Count"] = str(result.total_count)

    return result.data
