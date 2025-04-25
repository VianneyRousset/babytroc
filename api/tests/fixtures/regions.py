from typing import TypedDict

import pytest
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import services
from app.schemas.region.create import RegionCreate
from app.schemas.region.read import RegionRead


class RegionData(TypedDict):
    id: int
    name: str


@pytest.fixture
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
def regions(
    database: sqlalchemy.URL,
    regions_data: list[RegionData],
) -> list[RegionRead]:
    """Ensures the regions exists."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return [
            services.region.create_region(
                session,
                RegionCreate(**region),
            )
            for region in regions_data
        ]
