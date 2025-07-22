from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.router.v1.me.items.annotations import item_id_annotation
from app.routers.v1.auth import client_id_annotation
from app.schemas.loan.api import LoanApiQuery
from app.schemas.loan.query import LoanQueryFilter
from app.schemas.loan.read import LoanRead

from .annotations import loan_id_annotation
from .router import router


@router.get("", status_code=status.HTTP_200_OK)
def list_item_loans(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    request: Request,
    response: Response,
    query: Annotated[LoanApiQuery, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[LoanRead]:
    """List loans of the item owned by the client."""

    result = services.loan.list_loans(
        db=db,
        query_filter=LoanQueryFilter.model_validate(
            {
                **query.loan_query_filter.model_dump(),
                "owner_id": client_id,
                "item_id": item_id,
            }
        ),
        page_options=query.loan_query_page_options,
    )

    result.set_response_headers(response, request)

    return result.data


@router.get("/{loan_id}", status_code=status.HTTP_200_OK)
def get_client_loan(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    loan_id: loan_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRead:
    """Get loan where the client is the owner."""

    return services.loan.get_loan(
        db=db,
        loan_id=loan_id,
        query_filter=LoanQueryFilter(
            owner_id=client_id,
            item_id=item_id,
        ),
    )
