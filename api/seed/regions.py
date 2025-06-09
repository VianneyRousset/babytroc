import logging
from collections.abc import Iterable

import sqlalchemy
from tqdm import tqdm

import app
from app.schemas.region.create import RegionCreate as Region

logger = logging.getLogger("seed")


def check_regions(
    db: sqlalchemy.orm.Session,
) -> bool:
    """Returns True if some regions are present in the database."""

    logger.debug("Checking regions: started")
    regions = app.services.region.list_regions(db)
    logger.debug("%i regions found", len(regions))
    res = len(regions) > 0
    logger.debug("Checking regions: done")

    return res


def populate_regions(
    db: sqlalchemy.orm.Session,
    regions: Iterable[Region],
) -> None:
    """Populate regions."""

    logger.debug("Populating regions: started")

    for region in tqdm(regions):
        app.services.region.create_region(
            db=db,
            region_create=region,
        )

    logger.debug("Populating regions: done")
