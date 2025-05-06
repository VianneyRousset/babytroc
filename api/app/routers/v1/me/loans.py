from typing import Annotated

from fastapi import Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.loan.api import LoanApiQuery
from app.schemas.loan.query import LoanQueryFilter
from app.schemas.loan.read import LoanRead
from app.schemas.query import QueryPageOptions

from .me import router

loan_id_annotation = Annotated[
    int,
    Path(
        title="The ID of the loan.",
        ge=0,
    ),
]

# READ


@router.get("/loans", status_code=status.HTTP_200_OK)
def list_client_loans(
    client_id: client_id_annotation,
    response: Response,
    query: Annotated[LoanApiQuery, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[LoanRead]:
    """List loans where the client is the owner."""

    result = services.loan.list_loans(
        db=db,
        query_filter=LoanQueryFilter(
            owner_id=client_id,
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


@router.get("/loans/{loan_id}", status_code=status.HTTP_200_OK)
def get_client_loan(
    client_id: client_id_annotation,
    loan_id: loan_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRead:
    """Get loan where the client is the owner."""

    return services.loan.get_loan(
        db=db,
        loan_id=loan_id,
        query_filter=LoanQueryFilter(
            owner_id=client_id,
        ),
    )


# UPDATE


@router.post("/loans/{loan_id}/end", status_code=status.HTTP_200_OK)
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
