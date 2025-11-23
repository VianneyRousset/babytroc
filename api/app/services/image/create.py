from typing import IO

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import utils
from app.clients.networking import imgpush
from app.config import Config
from app.models.item.image import ItemImage
from app.schemas.image.read import ItemImageRead
from app.services.user.read import get_user

from .constants import MAX_DIMENSION


# TODO those image manipulation should be done asynchronously (e.g. by another process)
async def upload_image(
    config: Config,
    db: AsyncSession,
    *,
    owner_id: int,
    fp: IO[bytes],
) -> ItemImageRead:
    """Upload a new item image."""

    # load and process image
    image = utils.image.load_image(fp)
    image = utils.image.limit_image_size(image, MAX_DIMENSION)
    image = utils.image.apply_exif_orientation(image)
    image = utils.image.clear_exif(image)

    # serialize and upload image to imgpush
    fp = utils.image.serialize_image(image)
    resp = await imgpush.upload_image(config, fp)
    name = resp.name

    # create item in database
    stmt = insert(ItemImage).values(
        {
            "name": name,
            "owner_id": owner_id,
        }
    )

    try:
        item_image = (await db.execute(stmt)).unique().scalars().one()

    # If an IntegrityError is raised, it means either:
    # 1. The owner does not exist
    # 2. Unexpected error
    except IntegrityError as error:
        # raises UserNotFoundError if owner does not exist (1.)
        await get_user(
            db=db,
            user_id=owner_id,
        )

        # unexpected error (2.)
        raise error

    return ItemImageRead.model_validate(item_image)
