import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache_keys import TTL_REGIONS, key_regions
from app.clients.cache import Cache
from app.domains.region.errors import RegionNotFoundError
from app.models.item import Region
from app.domains.region.schemas.read import RegionRead


async def get_region(
    db: AsyncSession,
    region_id: int,
) -> RegionRead:
    """Get region with the given region id.

    Raises RegionNotFoundError if the region does not exists.
    """

    regions = await get_many_regions(
        db=db,
        region_ids={region_id},
    )

    return regions[0]


async def get_many_regions(
    db: AsyncSession,
    region_ids: set[int],
) -> list[RegionRead]:
    """Get all regions with the given region ids.

    Raises RegionNotFoundError if not all regions exist.
    """

    stmt = select(Region).where(Region.id.in_(region_ids))

    regions = (await db.execute(stmt)).unique().scalars().all()

    # If the number of queried regions  does not match the number of given region ids,
    # it means either:
    # 1. Some regions do not exist
    # 2. Unexpected error
    if len(regions) != len(region_ids):
        # check missing regions (1.)
        if missing_region_ids := region_ids - {reg.id for reg in regions}:
            raise RegionNotFoundError({"region_ids": missing_region_ids})

        # Unexpected error (2.)
        msg = (
            f"The number of queried regions ({len(regions)}) does not match the number "
            f"of given region ids ({len(region_ids)}). Unexpected reason"
        )
        raise RuntimeError(msg)

    return [RegionRead.model_validate(reg) for reg in regions]


async def list_regions(
    db: AsyncSession,
    cache: Cache,
) -> list[RegionRead]:
    """List all regions."""

    cached = await cache.get(key_regions())
    if cached is not None:
        return [RegionRead.model_validate(r) for r in json.loads(cached)]

    stmt = select(Region)

    regions = (await db.execute(stmt)).unique().scalars().all()

    result = [RegionRead.model_validate(reg) for reg in regions]

    await cache.set(
        key_regions(),
        json.dumps([r.model_dump(mode="json") for r in result]),
        ttl=TTL_REGIONS,
    )

    return result
