from typing import Annotated

from fastapi import Path, Query, Request, Response, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.loan.api import LoanRequestApiQuery
from app.schemas.loan.query import LoanRequestQueryFilter
from app.schemas.loan.read import LoanRequestRead
from app.schemas.query import QueryPageOptions

from .router import router

loan_request_id_annotation = Annotated[
    int,
    Path(
        title="The ID of the loan request.",
        ge=0,
    ),
]

# READ


@router.get("/requests", status_code=status.HTTP_200_OK)
def list_client_borrowing_loan_requests(
    request: Request,
    response: Response,
    query: Annotated[LoanRequestApiQuery, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[LoanRequestRead]:
    """List pending loan requests made by the client."""

    client_user_id = services.auth.check_auth(request)

    # get list of loan requests of the item
    result = services.loan.list_loan_requests(
        db=db,
        query_filter=LoanRequestQueryFilter(
            borrower_id=client_user_id,
            state=query.state,
        ),
        page_options=QueryPageOptions(
            order=["loan_request_id"],
            desc=True,
        ),
    )

    response.headers["X-Total-Count"] = str(result.total_count)

    return result.data


@router.get(
    "/requests/{loan_request_id}",
    status_code=status.HTTP_200_OK,
)
def get_client_borrowing_loan_request(
    request: Request,
    loan_request_id: int,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRequestRead:
    """Get loan request made by the client."""

    client_user_id = services.auth.check_auth(request)

    # get list of loan requests of the item
    return services.loan.get_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestQueryFilter(
            borrower_id=client_user_id,
        ),
    )
