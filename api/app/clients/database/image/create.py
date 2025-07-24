from sqlalchemy.orm import Session

from app.models.item import ItemImage


def create_image(
    db: Session,
    *,
    name: str,
    owner_id: int,
) -> ItemImage:
    """Create and insert image into database."""

    image = ItemImage(
        name=name,
        owner_id=owner_id,
    )

    return insert_image(db, image)


def insert_image(
    db: Session,
    image: ItemImage,
) -> ItemImage:
    """Insert image into the database."""

    # TODO handle owner does not exists
    db.add(image)

    db.flush()
    db.refresh(image)

    return image
