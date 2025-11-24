from typing import Annotated

from fastapi import Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.database import get_db_async_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.loan.read import LoanRequestRead

from .annotations import item_id_annotation
from .router import router

# CREATE


@router.post("/{item_id}/request", status_code=status.HTTP_201_CREATED)
async def create_loan_request(
    client_id: client_id_annotation,
    request: Request,
    item_id: item_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> LoanRequestRead:
    """Add a loan request of the item."""

    return await services.loan.create_loan_request(
        db=db,
        item_id=item_id,
        borrower_id=client_id,
    )


# DELETE


@router.delete("/{item_id}/request", status_code=status.HTTP_200_OK)
async def cancel_item_active_loan_request(
    client_id: client_id_annotation,
    request: Request,
    item_id: item_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> LoanRequestRead:
    """Add a loan request of the item."""

    return await services.loan.cancel_item_active_loan_request(
        db=db,
        item_id=item_id,
        borrower_id=client_id,
    )
