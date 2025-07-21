from sqlalchemy import delete, insert, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from app.errors.image import ItemImageNotFoundError
from app.errors.item import ItemNotFoundError
from app.errors.region import RegionNotFoundError
from app.models.item import Item
from app.models.item.image import ItemImageAssociation
from app.models.item.region import ItemRegionAssociation
from app.schemas.item.query import ItemQueryFilter
from app.schemas.item.read import ItemRead
from app.schemas.item.update import ItemUpdate


def update_item(
    db: Session,
    *,
    item_id: int,
    item_update: ItemUpdate,
    query_filter: ItemQueryFilter | None = None,
) -> ItemRead:
    """Update item with `item_id`."""

    # default empty query filter
    query_filter = query_filter or ItemQueryFilter()

    # update item fields
    update_item_stmt = query_filter.apply(
        update(Item)
        .where(Item.id == item_id)
        .values(item_update.as_sql_values(exclude={"images", "regions"}))
    ).returning(Item)

    # execute item update
    try:
        item = db.execute(update_item_stmt).unique().scalars().one()

    except NoResultFound as error:
        raise ItemNotFoundError({**query_filter.key, "id": item_id}) from error

    # delete and insert item-region associations
    if item_update.regions is not None:
        delete_item_region_associations_stmt = delete(ItemRegionAssociation).where(
            ItemRegionAssociation.item_id == item_id
        )
        db.execute(delete_item_region_associations_stmt)
        insert_item_region_associations_stmt = insert(ItemRegionAssociation).values(
            [
                {
                    "item_id": item_id,
                    "region_id": region_id,
                }
                for region_id in item_update.regions
            ]
        )

        # execute item-regions associations insert
        try:
            db.execute(insert_item_region_associations_stmt)

        except IntegrityError as error:
            raise RegionNotFoundError({"id": item_update.regions}) from error

    # delete and insert item-image associations
    if item_update.images is not None:
        delete_item_image_associations_stmt = delete(ItemImageAssociation).where(
            ItemImageAssociation.item_id == item_id
        )
        db.execute(delete_item_image_associations_stmt)
        insert_item_image_associations_stmt = insert(ItemImageAssociation).values(
            [
                {
                    "item_id": item_id,
                    "image_name": image_name,
                    "order": i,
                }
                for i, image_name in enumerate(item_update.images)
            ]
        )

        # execute item-images associations insert
        try:
            db.execute(insert_item_image_associations_stmt)

        except IntegrityError as error:
            raise ItemImageNotFoundError({"id": item_update.images}) from error

    return ItemRead.model_validate(item)
