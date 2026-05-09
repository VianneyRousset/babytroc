from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.category import services as category_services
from app.domains.region import services as region_services
from app.infrastructure.cache import get_cache
from app.infrastructure.cache_client import Cache
from app.infrastructure.database import get_db_session
from app.domains.category.schemas.read import CategoryRead
from app.domains.region.schemas.read import RegionRead

router = APIRouter()


@router.get("/regions", status_code=status.HTTP_200_OK)
async def list_regions(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> list[RegionRead]:
    """List regions."""

    return await region_services.list_regions(db, cache)


@router.get("/categories", status_code=status.HTTP_200_OK)
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> list[CategoryRead]:
    """List categories."""

    return await category_services.list_categories(db, cache)
