from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.category import services as category_services
from babytroc.domains.category.schemas.read import CategoryRead
from babytroc.domains.region import services as region_services
from babytroc.domains.region.schemas.read import RegionRead
from babytroc.infrastructure.cache import get_cache
from babytroc.infrastructure.cache_client import Cache
from babytroc.infrastructure.database import get_db_session

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
