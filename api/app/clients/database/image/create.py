from sqlalchemy.orm import Session

from app.clients.database.user import get_user
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

    # check owner exists
    if image.owner_id is not None:
        get_user(db, image.owner_id)

    db.add(image)

    db.flush()
    db.refresh(image)

    return image
