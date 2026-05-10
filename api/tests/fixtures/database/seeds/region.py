"""Reference region seed."""

from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.region.schemas.create import RegionCreate
from babytroc.domains.region.services import create_region
from tests.fixtures.database.infrastructure.chain import SeedContext


async def seed_reference_regions(db: AsyncSession, ctx: SeedContext) -> None:
    """Insert the two canonical test regions."""
    del ctx
    await create_region(db=db, region_create=RegionCreate(id=1, name="region1"))
    await create_region(db=db, region_create=RegionCreate(id=2, name="region2"))
