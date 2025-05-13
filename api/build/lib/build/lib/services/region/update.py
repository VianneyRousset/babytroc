from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.region.read import RegionRead
from app.schemas.region.update import RegionUpdate


def update_region(
    db: Session,
    region_id: int,
    region_update: RegionUpdate,
) -> RegionRead:
    """Update region with `region_id`."""

    # get region
    region = database.region.get_region(
        db=db,
        region_id=region_id,
    )

    # update region
    region = database.region.update_region(
        db=db,
        region=region,
        attributes=region_update.dict(),
    )

    return RegionRead.model_validate(region)
