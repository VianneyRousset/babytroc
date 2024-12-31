import io

from sqlalchemy.orm import Session

from app import config, utils
from app.clients import database
from app.clients.networking import imgpush
from app.schemas.image.read import ItemImageRead


def upload_image(
    db: Session,
    *,
    owner_id: int,
    fp: io.IOBase,
) -> ItemImageRead:
    """Upload a new item image."""

    # load and process image
    image = utils.image.load_image(fp)
    image = utils.image.limit_image_size(image, config.ITEM_IMAGE_MAX_DIMENSION)
    image = utils.image.apply_exif_orientation(image)
    image = utils.image.clear_exif(image)

    # serialize and upload image to imgpush
    fp = utils.image.serialize_image(image)
    name = imgpush.upload_image(fp).name

    # create item in database
    item = database.image.create_image(
        db=db,
        name=name,
        owner_id=owner_id,
    )

    return ItemImageRead.from_orm(item)
