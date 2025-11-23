from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.item.query import ItemReadQueryFilter
from app.schemas.loan.api import LoanRequestApiQuery
from app.schemas.loan.query import (
    LoanRequestReadQueryFilter,
    LoanRequestUpdateQueryFilter,
)
from app.schemas.loan.read import LoanRequestRead

from .annotations import item_id_annotation, loan_request_id_annotation
from .router import router

# READ


@router.get("/{item_id}/requests", status_code=status.HTTP_200_OK)
def list_client_item_loan_requests(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    item_id: item_id_annotation,
    query: Annotated[LoanRequestApiQuery, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[LoanRequestRead]:
    """List loan requests of the item owned by the client."""

    # get item to check it is owned by the client
    item = services.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=ItemReadQueryFilter(
            owner_id=client_id,
        ),
    )

    # get list of loan requests of the item
    result = services.loan.list_loan_requests(
        db=db,
        query_filter=LoanRequestReadQueryFilter.model_validate(
            {
                **query.loan_request_select_query_filter.model_dump(),
                "item_id": item.id,
            }
        ),
        page_options=query.loan_request_query_page_options,
    )

    result.set_response_headers(response, request)

    return result.data


@router.get(
    "/{item_id}/requests/{loan_request_id}",
    status_code=status.HTTP_200_OK,
)
def get_client_item_loan_request(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRequestRead:
    """Get client's item loan request by id."""

    # get item to check it is owned by the client
    item = services.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=ItemReadQueryFilter(
            owner_id=client_id,
        ),
    )

    return services.loan.get_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestReadQueryFilter(
            item_id=item.id,
        ),
    )


@router.post(
    "/{item_id}/requests/{loan_request_id}/accept",
    status_code=status.HTTP_200_OK,
)
def accept_client_item_loan_request(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRequestRead:
    """Accept client's item loan request."""

    return services.loan.accept_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestUpdateQueryFilter(
            item_id=item_id,
            owner_id=client_id,
        ),
    )


@router.post(
    "/{item_id}/requests/{loan_request_id}/reject",
    status_code=status.HTTP_200_OK,
)
def reject_client_item_loan_request(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> LoanRequestRead:
    """Reject client's item loan request."""

    return services.loan.reject_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestUpdateQueryFilter(
            item_id=item_id,
            owner_id=client_id,
        ),
    )
