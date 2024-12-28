from typing import Annotated

from fastapi import Query, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.loan.query import LoanRequestQueryFilter
from app.schemas.loan.read import LoanRequestRead
from app.schemas.query import QueryPageOptions

from .annotations import item_id_annotation, loan_request_id_annotation
from .router import router


# TODO check pagination parameters
@router.get("/items/{item_id}/requests", status_code=status.HTTP_200_OK)
def list_client_item_loan_requests(
    request: Request,
    item_id: item_id_annotation,
    page_options: Annotated[
        QueryPageOptions,
        Query(),
    ],
    db: Session = Depends(get_db_session),
) -> list[LoanRequestRead]:
    """List loan requests made for the client's item."""

    client_user_id = services.auth.check_auth(request)

    result = services.loan.list_loans(
        db=db,
        query_filter=LoanRequestQueryFilter(
            item_id=item_id,
            owner_id=client_user_id,
        ),
        page_options=page_options,
    )

    # TODO add pagination info in headers
    return result.data


@router.get(
    "/items/{item_id}/requests/{loan_request_id}",
    status_code=status.HTTP_200_OK,
)
def get_client_item_loan_request(
    request: Request,
    item_id: item_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Session = Depends(get_db_session),
) -> LoanRequestRead:
    """Get client's item loan request by id."""

    client_user_id = services.auth.check_auth(request)

    return services.loan.get_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestQueryFilter(
            item_id=item_id,
            owner_id=client_user_id,
        ),
    )


@router.post(
    "/items/{item_id}/requests/{loan_request_id}/accept",
    status_code=status.HTTP_200_OK,
)
def accept_client_item_loan_request(
    request: Request,
    item_id: item_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Session = Depends(get_db_session),
) -> LoanRequestRead:
    """Accept client's item loan request."""

    client_user_id = services.auth.check_auth(request)

    return services.loan.accept_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestQueryFilter(
            item_id=item_id,
            owner_id=client_user_id,
        ),
    )


@router.post(
    "/items/{item_id}/requests/{loan_request_id}/reject",
    status_code=status.HTTP_200_OK,
)
def reject_client_item_loan_request(
    request: Request,
    item_id: item_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Session = Depends(get_db_session),
) -> LoanRequestRead:
    """Reject client's item loan request."""

    client_user_id = services.auth.check_auth(request)

    return services.loan.reject_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestQueryFilter(
            item_id=item_id,
            owner_id=client_user_id,
        ),
    )
