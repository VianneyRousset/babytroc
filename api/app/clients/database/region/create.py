from typing import Optional

from sqlalchemy.orm import Session

from app.models.item import Region


def create_region(
    db: Session,
    *,
    name: str,
    region_id: Optional[int] = None,
) -> Region:
    """Create and insert region into database."""

    region = Region(
        id=region_id,
        name=name,
    )

    return insert_region(
        db=db,
        region=region,
    )


def insert_region(
    db: Session,
    region: Region,
) -> Region:
    """Insert region into database."""

    db.add(region)
    db.flush()
    db.refresh(region)
    return region
