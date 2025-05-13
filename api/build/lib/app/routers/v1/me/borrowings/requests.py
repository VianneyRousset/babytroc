from typing import Annotated

from fastapi import Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.loan.api import LoanRequestApiQuery
from app.schemas.loan.query import LoanRequestQueryFilter
from app.schemas.loan.read import LoanRead, LoanRequestRead
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
    client_id: client_id_annotation,
    response: Response,
    query: Annotated[LoanRequestApiQuery, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[LoanRequestRead]:
    """List pending loan requests made by the client."""

    # get list of loan requests of the item
    result = services.loan.list_loan_requests(
        db=db,
        query_filter=LoanRequestQueryFilter(
            borrower_id=client_id,
            states=query.states,
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
    client_id: client_id_annotation,
    loan_request_id: int,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRequestRead:
    """Get loan request made by the client."""

    # get list of loan requests of the item
    return services.loan.get_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestQueryFilter(
            borrower_id=client_id,
        ),
    )


@router.post(
    "/requests/{loan_request_id}/execute",
    status_code=status.HTTP_201_CREATED,
)
def execute_loan_request(
    client_id: client_id_annotation,
    loan_request_id: int,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRead:
    """Create a loan from an accepted loan request."""

    # get list of loan requests of the item
    return services.loan.execute_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestQueryFilter(
            borrower_id=client_id,
        ),
    )
