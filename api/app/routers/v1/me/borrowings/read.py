from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.loan.api import LoanApiQuery
from app.schemas.loan.query import LoanReadQueryFilter
from app.schemas.loan.read import LoanRead

from .annotations import loan_id_annotation
from .router import router


@router.get("", status_code=status.HTTP_200_OK)
async def list_client_borrowings(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    query: Annotated[LoanApiQuery, Query()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[LoanRead]:
    """List loans where the client is the borrower."""

    result = await services.loan.list_loans(
        db=db,
        query_filter=LoanReadQueryFilter.model_validate(
            {
                **query.loan_select_query_filter.model_dump(),
                "borrower_id": client_id,
            }
        ),
        page_options=query.loan_query_page_options,
    )

    result.set_response_headers(response, request)

    return result.data


@router.get("/{loan_id}", status_code=status.HTTP_200_OK)
async def get_client_borrowing(
    client_id: client_id_annotation,
    loan_id: loan_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoanRead:
    """Get loan where the client is the owner."""

    return await services.loan.get_loan(
        db=db,
        loan_id=loan_id,
        query_filter=LoanReadQueryFilter(
            owner_id=client_id,
        ),
    )
