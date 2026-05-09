from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.image.errors import ItemImageNotFoundError, ItemImageNotOwnedError
from app.domains.item.models.image import ItemImage
from app.shared.schemas import Base as SchemaBase
from app.domains.image.schemas.read import ItemImageRead


class CheckImageOwner(SchemaBase):
    image_name: str
    owner_id: int


async def get_many_images(
    db: AsyncSession,
    image_names: set[str],
) -> list[ItemImageRead]:
    """Get all item images with the given image names.

    Raises ItemImageNotFoundError if not all images exist.
    """

    stmt = select(ItemImage).where(ItemImage.name.in_(image_names))

    images = (await db.execute(stmt)).unique().scalars().all()

    if len(images) != len(image_names):
        if missing_image_names := image_names - {img.name for img in images}:
            raise ItemImageNotFoundError({"image_names": missing_image_names})

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
