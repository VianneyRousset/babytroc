import logging
from collections.abc import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from tqdm import tqdm

import app
from app.infrastructure.cache_client import NullCache
from app.domains.region.schemas.create import RegionCreate as Region

logger = logging.getLogger("seed")

_cache = NullCache()


async def check_regions(
    db: AsyncSession,
) -> bool:
    """Returns True if some regions are present in the database."""

    logger.debug("Checking regions: started")
    regions = await app.services.region.list_regions(db, _cache)
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
        await app.services.region.create_region(
            db=db,
            region_create=region,
        )

    logger.debug("Populating regions: done")
