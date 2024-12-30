from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.image import ItemImageNotFoundError
from app.models.item import ItemImage


def get_image(
    db: Session,
    image_id: int,
) -> ItemImage:
    """Get image with `image_id` from database."""

    stmt = select(ItemImage).where(ItemImage.id == image_id)

    try:
        return (db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise ItemImageNotFoundError({"id": image_id}) from error


def get_image_by_name(
    db: Session,
    name: str,
) -> ItemImage:
    """Get image with `name` from database."""

    stmt = select(ItemImage).where(ItemImage.name == name)

    try:
        return (db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise ItemImageNotFoundError({"name": name}) from error
