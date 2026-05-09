from typing import Annotated

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.loan import services as loan_services
from app.infrastructure.cache import get_cache
from app.infrastructure.cache_client import Cache
from app.infrastructure.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.domains.loan.schemas.query import LoanRequestUpdateQueryFilter
from app.domains.loan.schemas.read import LoanRead, LoanRequestRead

from .annotations import loan_request_id_annotation
from .router import router


@router.post("/{loan_request_id}/cancel", status_code=status.HTTP_201_CREATED)
async def cancel_borrowing_loan_request(
    client_id: client_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> LoanRequestRead:
    """Cancel pending loan request where the client is the borrower."""

    return await loan_services.cancel_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestUpdateQueryFilter(
            borrower_id=client_id,
        ),
        cache=cache,
    )


@router.post("/{loan_request_id}/execute", status_code=status.HTTP_201_CREATED)
async def execute_loan_request(
    client_id: client_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> LoanRead:
    """Create a loan from an accepted loan request."""

    # get list of loan requests of the item
    return await loan_services.execute_loan_request(
        db=db,
        loan_request_id=loan_request_id,
        query_filter=LoanRequestUpdateQueryFilter(
            borrower_id=client_id,
        ),
        cache=cache,
    )
