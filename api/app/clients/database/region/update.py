from typing import Any, Mapping

from sqlalchemy.orm import Session

from app.models.item import Region


def update_region(
    db: Session,
    region: Region,
    attributes: Mapping[str, Any],
) -> Region:
    """Update the given `attributes` of `region`."""

    for key, value in attributes.items():
        setattr(region, key, value)

    db.flush()
    db.refresh(region)

    return region
