from collections.abc import Collection
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.clients.database import dbutils
from app.errors.exception import ItemImageNotFoundError
from app.models.item import ItemImage


async def get_image(
    db: Session,
    image_id: int,
    *,
    load_attributes: Optional[Collection[dbutils.LoadableAttrType]] = None,
    options: Optional[Collection[dbutils.ExecutableOption]] = None,
) -> ItemImage:
    """Get image with `image_id` from database."""

    stmt = select(ItemImage).where(ItemImage.id == image_id)
    stmt = dbutils.add_default_query_options(
        stmt=stmt,
        load_attributes=load_attributes,
        options=options,
    )

    try:
        image = (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        raise ItemImageNotFoundError({"image_id": image_id}) from error

    return image


async def delete_image(db: Session, image_id: int) -> None:
    """Delete the image with `image_id` from database."""

    user = await get_image(db, image_id)

    await db.delete(user)
    await db.flush()
