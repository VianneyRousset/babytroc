from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.region.create import RegionCreate
from app.schemas.region.read import RegionRead


def create_region(
    db: Session,
    region_create: RegionCreate,
) -> RegionRead:
    """Create a region."""

    return database.region.create_region(
        db=db,
        region_id=region_create.id,
        name=region_create.name,
    )
