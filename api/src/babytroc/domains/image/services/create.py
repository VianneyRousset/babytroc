import asyncio
import uuid
from io import BytesIO

import PIL.Image
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.image.errors import (
    ImagePixelLimitError,
    ImageTooLargeError,
    InvalidImageError,
)
from babytroc.domains.image.schemas.read import ItemImageRead
from babytroc.domains.item.models.image import ItemImage
from babytroc.domains.user.services.read import get_user
from babytroc.infrastructure import storage
from babytroc.infrastructure.config import Config
from babytroc.shared import image as image_utils


async def upload_image(
    config: Config,
    db: AsyncSession,
    semaphore: asyncio.Semaphore,
    *,
    owner_id: int,
    data: bytes,
) -> ItemImageRead:
    """Upload a new item image. Generates webp variants and stores in S3."""

    if len(data) > config.image.max_upload_bytes:
        raise ImageTooLargeError(
            actual=len(data),
            limit=config.image.max_upload_bytes,
        )

    async with semaphore:
        try:
            variants = await asyncio.to_thread(
                image_utils.generate_webp_variants,
                BytesIO(data),
            )
        except PIL.Image.DecompressionBombError as error:
            raise ImagePixelLimitError(config.image.max_pixels) from error
        except (PIL.UnidentifiedImageError, OSError, SyntaxError) as error:
            raise InvalidImageError() from error

    name = uuid.uuid4().hex

    await storage.upload_image_variants(
        config=config.s3,
        name=name,
        variants=variants,
    )

    stmt = (
        insert(ItemImage)
        .values(
            {
                "name": name,
                "owner_id": owner_id,
            },
        )
        .returning(ItemImage)
    )

    try:
        res = await db.execute(stmt)
        item_image = res.unique().scalars().one()

    except IntegrityError as error:
        await get_user(
            db=db,
            user_id=owner_id,
        )
        raise error

    return ItemImageRead.model_validate(item_image)
