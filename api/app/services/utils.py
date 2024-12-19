from sqlalchemy.orm import Session

from app import config
from app.clients import database, dicebear
from app.schemas.region import RegionCreate, RegionRead


async def generate_avatar(
    size: int,
    seed: str,
) -> str:
    """Create an avatar of given `size` from `seed`."""

    return await dicebear.generate_avatar(
        size=size,
        seed=seed,
        scale=config.avatar.scale,
        radius=config.avatar.radius,
        bg=config.avatar.bg,
        fg=config.avatar.fg,
    )


async def create_region(
    db: Session,
    region_create: RegionCreate,
) -> RegionRead:
    """Create a region."""

    return await database.item.create_region(
        db=db,
        region_id=region_create.id,
        name=region_create.name,
    )


async def list_regions(
    db: Session,
) -> list[RegionRead]:
    """List all regions."""

    return [
        RegionRead.from_orm(region)
        for region in await database.item.list_regions(db=db)
    ]
