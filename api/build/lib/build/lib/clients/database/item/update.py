from typing import Any

from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.orm import Session

from app.clients.database.image import get_image
from app.clients.database.region import get_region
from app.models.item import Item


def update_item(
    db: Session,
    item: Item,
    attributes: dict[str, Any],
) -> Item:
    """Update the given `attributes` of `item`."""

    if "regions" in attributes:
        attributes["regions"] = [
            get_region(db, region_id) for region_id in attributes["regions"]
        ]

    if "images" in attributes:
        attributes["images"] = [get_image(db, name) for name in attributes["images"]]

    if "targeted_age_months" in attributes:
        attributes["targeted_age_months"] = Range(
            *attributes["targeted_age_months"], bounds="[]"
        )

    for key, value in attributes.items():
        setattr(item, key, value)

    db.flush()
    db.refresh(item)

    return item
