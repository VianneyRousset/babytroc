from typing import Annotated

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.loan import services as loan_services
from app.infrastructure.cache import get_cache
from app.infrastructure.cache_client import Cache
from app.infrastructure.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.domains.loan.schemas.query import LoanUpdateQueryFilter
from app.domains.loan.schemas.read import LoanRead

from .annotations import loan_id_annotation
from .router import router


@router.post("/{loan_id}/end", status_code=status.HTTP_200_OK)
async def end_client_loan(
    client_id: client_id_annotation,
    loan_id: loan_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> LoanRead:
    """End the loan where the client is the owner."""

    return await loan_services.end_loan(
        db=db,
        loan_id=loan_id,
        query_filter=LoanUpdateQueryFilter(
            owner_id=client_id,
        ),
        cache=cache,
    )
