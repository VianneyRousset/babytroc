from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.routers.v1.me.items.annotations import item_id_annotation
from app.schemas.loan.api import LoanRequestApiQuery
from app.schemas.loan.query import LoanRequestReadQueryFilter
from app.schemas.loan.read import LoanRequestRead

from .annotations import loan_request_id_annotation
from .router import router


@router.get("", status_code=status.HTTP_200_OK)
def list_loan_requests_for_items_owned_by_the_client(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    request: Request,
    response: Response,
    query: Annotated[LoanRequestApiQuery, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[LoanRequestRead]:
    """List loan request of the item owned by the client."""

    result = services.loan.list_loan_requests(
        db=db,
        query_filter=LoanRequestReadQueryFilter.model_validate(
            {
                **query.loan_request_select_query_filter.model_dump(),
                "item_id": item_id,
                "owner_id": client_id,
            }
        ),
        page_options=query.loan_request_query_page_options,
    )

    result.set_response_headers(response, request)

    return result.data


@router.get("/{loan_request_id}", status_code=status.HTTP_200_OK)
def get_client_loan_request(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRequestRead:
    """Get loan request of the item owned by the client."""

    return services.loan.get_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestReadQueryFilter(
            item_id=item_id,
            owner_id=client_id,
        ),
    )
