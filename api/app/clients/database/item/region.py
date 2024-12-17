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
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> list[Region]:
    """List regions from database."""

    stmt = select(Region)
    stmt = dbutils.add_default_query_options(
        stmt=stmt,
        load_attributes=load_attributes,
        options=options,
    )

    return (await db.execute(stmt)).unique().scalars().all()


async def get_region(
    db: Session,
    region_id: int,
    *,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> Region:
    """Get region with `region_id` from database."""

    stmt = select(Region).where(Region.id == region_id)
    stmt = dbutils.add_default_query_options(
        stmt=stmt,
        load_attributes=load_attributes,
        options=options,
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
