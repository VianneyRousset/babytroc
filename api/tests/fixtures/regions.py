from typing import TypedDict

import pytest
from sqlalchemy.orm import sessionmaker

from app import services
from app.schemas.region.create import RegionCreate
from app.schemas.region.read import RegionRead


class RegionData(TypedDict):
    id: int
    name: str


@pytest.fixture(scope="class")
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


@pytest.fixture(scope="class")
def regions(
    database_sessionmaker: sessionmaker,
    regions_data: list[RegionData],
) -> list[RegionRead]:
    """Ensures the regions exists."""

    with database_sessionmaker.begin() as session:
        return [
            services.region.create_region(
                session,
                RegionCreate(**region),
            )
            for region in regions_data
        ]
