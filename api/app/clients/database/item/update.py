from typing import Any, Mapping

from sqlalchemy.orm import Session

from app.models.item import Item, ItemImage

from .region import get_region


def update_item(
    db: Session,
    item: Item,
    attributes: Mapping[str, Any],
) -> Item:
    """Update the given `attributes` of `item`."""

    # create required images
    if "images" in attributes:
        attributes["images"] = [ItemImage(name=name) for name in attributes["images"]]

    # TODO should raise 404 or something else ?
    if "regions" in attributes:
        attributes["regions"] = [
            get_region(
                db=db,
                region_id=region_id,
            )
            for region_id in attributes["regions"]
        ]

    for key, value in attributes.items():
        setattr(item, key, value)

    db.flush()
    db.refresh(item)

    return item
