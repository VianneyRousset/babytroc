from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.loan import services as loan_services
from app.infrastructure.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.domains.loan.schemas.api import LoanRequestApiQuery
from app.domains.loan.schemas.query import LoanRequestReadQueryFilter
from app.domains.loan.schemas.read import LoanRequestRead

from .annotations import loan_request_id_annotation
from .router import router


@router.get("", status_code=status.HTTP_200_OK)
async def list_loan_requests_for_items_owned_by_the_client(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    query: Annotated[LoanRequestApiQuery, Query()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[LoanRequestRead]:
    """List loan requests where the client is the owner."""

    result = await loan_services.list_loan_requests(
        db=db,
        query_filter=LoanRequestReadQueryFilter.model_validate(
            {
                **query.loan_request_select_query_filter.model_dump(),
                "owner_id": client_id,
            }
        ),
        page_options=query.loan_request_query_page_options,
    )

    result.set_response_headers(response, request)

    return result.data


@router.get("/{loan_request_id}", status_code=status.HTTP_200_OK)
async def get_client_loan_request(
    client_id: client_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoanRequestRead:
    """Get loan request where the client is the owner."""

    return await loan_services.get_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestReadQueryFilter(
            owner_id=client_id,
        ),
    )
