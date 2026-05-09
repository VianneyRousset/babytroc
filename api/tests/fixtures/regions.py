from typing import TypedDict

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.region import services as region_services
from babytroc.domains.region.schemas.read import RegionRead
from babytroc.infrastructure.cache_client import NullCache


class RegionData(TypedDict):
    id: int
    name: str


@pytest.fixture(scope="session")
def regions_data() -> list[RegionData]:
    """Regions data."""
    return [
        {
            "id": 1,
            "name": "region1",
        },
        {
            "id": 2,
            "name": "region2",
        },
    ]


@pytest.fixture
async def regions(
    database_sessionmaker: async_sessionmaker,
) -> list[RegionRead]:
    """Fetches the pre-seeded regions."""

    async with database_sessionmaker.begin() as session:
        return await region_services.list_regions(session, NullCache())
