import logging
from collections.abc import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from tqdm import tqdm

from app.domains.region.schemas.create import RegionCreate as Region
from app.domains.region.services import create_region, list_regions
from app.infrastructure.cache_client import NullCache

logger = logging.getLogger("seed")

_cache = NullCache()


async def check_regions(
    db: AsyncSession,
) -> bool:
    """Returns True if some regions are present in the database."""

    logger.debug("Checking regions: started")
    regions = await list_regions(db, _cache)
    logger.debug("%i regions found", len(regions))
    res = len(regions) > 0
    logger.debug("Checking regions: done")

    return res


async def populate_regions(
    db: AsyncSession,
    regions: Iterable[Region],
) -> None:
    """Populate regions."""

    logger.debug("Populating regions: started")

    for region in tqdm(regions):
        await create_region(
            db=db,
            region_create=region,
        )

    logger.debug("Populating regions: done")
