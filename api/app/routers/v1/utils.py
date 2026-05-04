from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.cache import get_cache
from app.clients.cache import Cache
from app.database import get_db_session
from app.schemas.category.read import CategoryRead
from app.schemas.region.read import RegionRead

router = APIRouter()


@router.get("/regions", status_code=status.HTTP_200_OK)
async def list_regions(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> list[RegionRead]:
    """List regions."""

    return await services.region.list_regions(db, cache)


@router.get("/categories", status_code=status.HTTP_200_OK)
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> list[CategoryRead]:
    """List categories."""

    return await services.category.list_categories(db, cache)
