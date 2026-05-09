from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from babytroc.domains.image.errors import ItemImageNotFoundError
from babytroc.domains.item.models import ItemImage


def get_image(
    db: Session,
    name: str,
) -> ItemImage:
    """Get image with `name` from database."""

    stmt = select(ItemImage).where(ItemImage.name == name)

    try:
        return db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        raise ItemImageNotFoundError({"name": name}) from error
