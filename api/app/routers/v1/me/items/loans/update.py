from typing import Annotated

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.database import get_db_async_session
from app.routers.v1.auth import client_id_annotation
from app.routers.v1.me.items.annotations import item_id_annotation
from app.schemas.loan.query import LoanUpdateQueryFilter
from app.schemas.loan.read import LoanRead

from .annotations import loan_id_annotation
from .router import router


@router.post("/{loan_id}/end", status_code=status.HTTP_200_OK)
async def end_client_loan(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    loan_id: loan_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> LoanRead:
    """End the loan of the item owned by the client."""

    return await services.loan.end_loan(
        db=db,
        loan_id=loan_id,
        query_filter=LoanUpdateQueryFilter(
            item_id=item_id,
            owner_id=client_id,
        ),
    )
