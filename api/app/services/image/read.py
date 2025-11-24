from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.networking import imgpush
from app.config import Config
from app.errors.image import ItemImageNotFoundError, ItemImageNotOwnedError
from app.models.item.image import ItemImage
from app.schemas.base import Base as SchemaBase
from app.schemas.image.read import ItemImageRead


class CheckImageOwner(SchemaBase):
    image_name: str
    owner_id: int


async def get_image_data(
    config: Config,
    image_name: str,
    *,
    size: int | None = None,
) -> bytes:
    """Get item by name."""

    # get item from databse
    image = await imgpush.get_image(
        config=config,
        name=image_name,
        size=size,
    )

    return image


async def get_many_images(
    db: AsyncSession,
    image_names: set[str],
) -> list[ItemImageRead]:
    """Get all item images with the given image names.

    Raises ItemImageNotFoundError if not all images exist.
    """

    stmt = select(ItemImage).where(ItemImage.name.in_(image_names))

    images = (await db.execute(stmt)).unique().scalars().all()

    # If the number of image read is different than the number of given image
    # names, it means either:
    # 1. Some images do not exists
    # 2. Unexpected error
    if len(images) != len(image_names):
        # some images do not exist (1.)
        if missing_image_names := image_names - {img.name for img in images}:
            raise ItemImageNotFoundError({"image_names": missing_image_names})

        # unexpected error
        msg = (
            "The number of images read does not match the number of image names. "
            "Unexpected reason"
        )
        raise RuntimeError(msg)

    return [ItemImageRead.model_validate(img) for img in images]


async def check_image_owners(
    db: AsyncSession,
    image_owners: list[CheckImageOwner],
) -> None:
    """Raises ItemImageNotOwnedError if any of the given images is not owner by user.

    Also raises ItemImageNotFoundError if not all images exist.
    """

    images = await get_many_images(
        db=db,
        image_names={a.image_name for a in image_owners},
    )

    if missing_image_owners := (
        {(a.image_name, a.owner_id) for a in image_owners}
        - {(img.name, img.owner_id) for img in images}
    ):
        raise ItemImageNotOwnedError(missing_image_owners)
