from collections.abc import Collection
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.clients.database import dbutils
from app.errors.exception import RegionNotFoundError
from app.models.item import Region


async def create_region(
    db: Session,
    *,
    name: str,
) -> Region:
    """Create and insert region into database."""

    region = Region(name=name)

    return await insert_region(
        db=db,
        region=region,
    )


async def insert_region(
    db: Session,
    region: Region,
) -> Region:
    """Insert region into database."""

    db.add(region)
    await db.flush()
    await db.refresh(region)
    return region


async def list_regions(
    db: Session,
    *,
    load_relationships: Optional[Collection[str]] = None,
) -> list[Region]:
    """List regions from database."""

    stmt = select(Region)
    stmt = dbutils.load_relationships(
        stmt=stmt,
        entity=Region,
        load_relationships=load_relationships,
    )

    return (await db.execute(stmt)).unique().scalars().all()


async def get_region(
    db: Session,
    region_id: int,
    *,
    load_relationships: Optional[Collection[str]] = None,
) -> Region:
    """Get region with `region_id` from database."""

    stmt = select(Region).where(Region.id == region_id)
    stmt = dbutils.load_relationships(
        stmt=stmt,
        entity=Region,
        load_relationships=load_relationships,
    )

    try:
        region = (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise RegionNotFoundError({"region_id": region_id}) from error

    return region


async def delete_region(db: Session, region_id: int) -> None:
    """Delete the region with `region_id` from database."""

    user = await get_region(db, region_id)

    await db.delete(user)
    await db.flush()
