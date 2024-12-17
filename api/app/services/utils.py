from sqlalchemy.orm import Session

from app import config
from app.clients import database, dicebear
from app.schemas.region import RegionRead


async def generate_avatar(
    size: int,
    seed: str,
) -> str:
    """Create an avatar of given `size` from `seed`."""

    return dicebear.generate_avatar(
        size=size,
        seed=seed,
        scale=config.avatar.scale,
        radius=config.avatar.radius,
        bg=config.avatar.bg,
        fg=config.avatar.fg,
    )


async def list_regions(
    db: Session,
) -> list[RegionRead]:
    """List all regions."""

    return [
        RegionRead.from_orm(region)
        for region in await database.item.list_regions(db=db)
    ]
