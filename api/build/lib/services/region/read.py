from sqlalchemy.orm import Session

from app.clients import database
from app.schemas.region.read import RegionRead


def list_regions(
    db: Session,
) -> list[RegionRead]:
    """List all regions."""

    return [
        RegionRead.model_validate(region) for region in database.region.list_regions(db)
    ]
