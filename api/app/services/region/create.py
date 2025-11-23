from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item.region import Region
from app.schemas.region.create import RegionCreate
from app.schemas.region.read import RegionRead


async def create_region(
    db: AsyncSession,
    region_create: RegionCreate,
) -> RegionRead:
    """Create a region."""

    regions = await create_many_regions(
        db=db,
        region_creates=[region_create],
    )

    return regions[0]


async def create_many_regions(
    db: AsyncSession,
    region_creates: list[RegionCreate],
) -> list[RegionRead]:
    """Create many regions."""

    data = [
        {"id": reg.id, "name": reg.name} if reg.id is not None else {"name": reg.name}
        for reg in region_creates
    ]

    stmt = insert(Region).values(data).returning(Region)

    regions = (await db.execute(stmt)).unique().scalars().all()

    if len(regions) != len(region_creates):
        msg = (
            "The number of created regions does not match the number of given "
            "region creates. The reason is unexpected."
        )
        raise RuntimeError(msg)

    return [RegionRead.model_validate(reg) for reg in regions]
