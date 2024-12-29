from typing import Annotated
from app.utils import set_query_param
from fastapi import Query, Request, status, Response
from app.schemas.loan.api import LoanRequestApiQuery

from fastapi import Body, Path, Query, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.loan.create import LoanRequestCreate
from app.schemas.loan.query import LoanRequestQueryFilter
from app.schemas.loan.read import LoanRead, LoanRequestRead
from app.schemas.query import QueryPageOptions

from .me import router

loan_request_id_annotation = Annotated[
    int,
    Path(
        title="The ID of the loan request.",
        ge=0,
    ),
]


@router.post("/requests", status_code=status.HTTP_201_CREATED)
def create_loan_request(
    request: Request,
    loan_request_create: Annotated[
        LoanRequestCreate,
        Body(
            title="Loan request creation fields.",
        ),
    ],
    db: Session = Depends(get_db_session),
) -> LoanRequestRead:
    """Create a loan request where the client is the borrower."""

    client_user_id = services.auth.check_auth(request)

    return services.loan.create_loan_request(
        db=db,
        borrower_user_id=client_user_id,
        loan_request_create=loan_request_create,
    )


@router.get("/requests", status_code=status.HTTP_200_OK)
def list_client_loan_requests(
    request: Request,
    response: Response,
    query: Annotated[LoanRequestApiQuery, Query()],
    db: Session = Depends(get_db_session),
) -> list[LoanRequestRead]:
    """List loan requests made by the client."""

    client_user_id = services.auth.check_auth(request)

    # get list of loan requests where the client is the borrower
    result = services.loan.list_loan_requests(
        db=db,
        query_filter=LoanRequestQueryFilter(
            borrower_id=client_user_id,
            state=query.state,
        ),
        page_options=QueryPageOptions(
            limit=query.n,
            order=["loan_request_id"],
            cursor={"loan_request_id": query.cid},
            desc=True,
        ),
    )

    query_params = request.query_params
    for k, v in result.next_cursor().items():
        # rename query parameters
        k = {
            "loan_request_id": "cid",
        }[k]

        query_params = set_query_param(query_params, k, v)

    response.headers["Link"] = f'<{request.url.path}?{query_params}>; rel="next"'

    response.headers["X-Total-Count"] = str(result.total_count)

    return result.data


@router.get("/requests/{loan_request_id}", status_code=status.HTTP_200_OK)
def get_client_loan_request(
    request: Request,
    loan_request_id: loan_request_id_annotation,
    db: Session = Depends(get_db_session),
) -> LoanRequestRead:
    """Get loan request made by the client."""

    client_user_id = services.auth.check_auth(request)

    return services.loan.get_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestQueryFilter(
            borrower_id=client_user_id,
        ),
    )


@router.delete("/requests/{loan_request_id}", status_code=status.HTTP_200_OK)
def cancel_client_loan_request(
    request: Request,
    loan_request_id: loan_request_id_annotation,
    db: Session = Depends(get_db_session),
):
    """Cancel client loan request."""

    client_user_id = services.auth.check_auth(request)

    return services.loan.cancel_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestQueryFilter(
            borrower_id=client_user_id,
        ),
    )


@router.post("/request/{loan_request_id}/confirm", status_code=status.HTTP_200_OK)
def execute_loan_request(
    request: Request,
    loan_request_id: loan_request_id_annotation,
    db: Session = Depends(get_db_session),
) -> LoanRead:
    """Create a loan from the loan request.

    The loan request state must be `accepted`.
    """

    client_user_id = services.auth.check_auth(request)

    return services.loan.execute_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestQueryFilter(
            borrower_id=client_user_id,
        ),
    )
