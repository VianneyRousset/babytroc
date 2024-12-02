from datetime import datetime
from typing import Annotated, Optional

from fastapi import Body, Path, Query, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.loan import LoanRead, LoanRequestCreate, LoanRequestRead

from .me import router

loan_request_id_annotation = (
    Annotated[
        int,
        Path(
            title="The ID of the loan request",
            ge=0,
        ),
    ],
)


@router.post("/requests", status_code=status.HTTP_201_CREATED)
async def create_loan_request(
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

    return services.items.create_loan_request(
        db=db,
        borrower_user_id=client_user_id,
        loan_request_create=loan_request_create,
    )


@router.get("/requests", status_code=status.HTTP_200_OK)
async def list_client_requests(
    request: Request,
    before: Annotated[
        Optional[int],
        Query(
            title="Select all requests with creation date before the item with this id",
        ),
    ] = None,
    count: Annotated[
        Optional[int],
        Query(
            title="Maximum number of requests to return",
            ge=0,
        ),
    ] = None,
    db: Session = Depends(get_db_session),
) -> list[LoanRequestRead]:
    """List loan requests made by the client ordered by inversed creation date."""

    client_user_id = services.auth.check_auth(request)

    return await services.loans.list_user_loan_requests(
        db=db,
        user_id=client_user_id,
        created_before_item_id=before,
        count=count,
    )


@router.get("/requests/{loan_request_id}", status_code=status.HTTP_200_OK)
async def get_client_loan_request_by_id(
    request: Request,
    loan_request_id: loan_request_id_annotation,
    db: Session = Depends(get_db_session),
) -> LoanRequestRead:
    """Get client loan request by id."""

    client_user_id = services.auth.check_auth(request)

    return await services.loans.get_user_loan_request_by_id(
        db=db,
        user_id=client_user_id,
        loan_request_id=loan_request_id,
    )


@router.delete("/requests/{loan_request_id}", status_code=status.HTTP_200_OK)
async def delete_client_loan_request(
    request: Request,
    loan_request_id: loan_request_id_annotation,
    db: Session = Depends(get_db_session),
):
    """Cancel client loan request."""

    client_user_id = services.auth.check_auth(request)

    return await services.loans.cancel_user_loan_request(
        db=db,
        user_id=client_user_id,
        loan_request_id=loan_request_id,
    )


@router.post("/request/{loan_request_id}/confirm", status_code=status.HTTP_200_OK)
async def create_loan_from_client_loan_request(
    request: Request,
    loan_request_id: loan_request_id_annotation,
    db: Session = Depends(get_db_session),
) -> LoanRead:
    """Create a loan from the loan request."""

    client_user_id = services.auth.check_auth(request)

    return services.loans.create_loan_from_user_loan_request(
        db=db,
        user_id=client_user_id,
        loan_request_id=loan_request_id,
    )
