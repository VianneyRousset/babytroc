import uuid
from typing import IO

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import utils
from app.clients.storage import s3
from app.config import Config
from app.models.item.image import ItemImage
from app.domains.image.schemas.read import ItemImageRead
from app.services.user.read import get_user


async def upload_image(
    config: Config,
    db: AsyncSession,
    *,
    owner_id: int,
    fp: IO[bytes],
) -> ItemImageRead:
    """Upload a new item image. Generates 3 webp variants and stores in S3."""

    # Process image and generate webp variants
    variants = utils.image.generate_webp_variants(fp)

    # Generate a unique name
    name = uuid.uuid4().hex

    # Upload all variants to S3
    await s3.upload_image_variants(
        config=config.s3,
        name=name,
        variants=variants,
    )

    # Create item image record in database
    stmt = (
        insert(ItemImage)
        .values(
            {
                "name": name,
                "owner_id": owner_id,
            }
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
