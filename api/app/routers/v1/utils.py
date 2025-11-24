from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.database import get_db_session
from app.schemas.region.read import RegionRead

router = APIRouter()


@router.get("/regions", status_code=status.HTTP_200_OK)
async def list_regions(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[RegionRead]:
    """List regions."""

    return await services.region.list_regions(db)
