from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.region import RegionNotFoundError
from app.models.item import Region


def list_regions(
    db: Session,
) -> list[Region]:
    """List regions from database."""

    stmt = select(Region)

    return list(db.execute(stmt).scalars().all())


def get_region(
    db: Session,
    region_id: int,
) -> Region:
    """Get region with `region_id` from database."""

    stmt = select(Region).where(Region.id == region_id)

    try:
        return db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        raise RegionNotFoundError({"id": region_id}) from error
