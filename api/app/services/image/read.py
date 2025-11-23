from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.networking import imgpush
from app.config import Config
from app.errors.image import ItemImageNotFoundError
from app.models.item.image import ItemImage


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


async def check_images_exist(
    db: AsyncSession,
    image_names: list[str],
    *,
    owner_ids: list[int] | None = None,
) -> None:
    """Raises ImageNotFoundError if any of the given images does not exist.

    If the list of user_ids `owner_ids` is given, each image name is checked to be owned
    by the given owner. `owner_ids` has to be of the same length as `image_names`.
    """

    if len(set(image_names)) != len(image_names):
        msg = "Non-unique image names"
        raise ValueError(msg)

    stmt = select(ItemImage.name)

    if owner_ids:
        # check number of owner_ids
        if len(owner_ids) != len(image_names):
            msg = (
                "The number of owner_ids must be the same as the number of image names."
            )
            raise ValueError(msg)

        stmt = stmt.where(
            tuple_(ItemImage.name, ItemImage.owner_id).in_(
                zip(image_names, owner_ids, strict=True)
            )
        )

    else:
        stmt = stmt.where(ItemImage.name.in_(image_names))

    read_item_images = (await db.execute(stmt)).unique().scalars().all()

    # If the number of image read is different than the number of given image
    # names, it means either:
    # 1. Some images do not exists or is not owned by the given user
    # 2. Unexpected error
    if len(read_item_images) != len(image_names):
        # some images do not exist (1.)
        if missing_image_names := image_names - {img.name for img in read_item_images}:
            raise ItemImageNotFoundError({"image_names": missing_image_names})

        # unexpected error
        msg = (
            "The number of images read does not match the number of image names. "
            "Unexpected reason"
        )
        raise RuntimeError(msg)
