from sqlalchemy import and_, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.errors.item import ItemNotFoundError
from app.models.item import Item, ItemLike, ItemSave
from app.schemas.item.query import ItemQueryFilter
from app.schemas.item.read import ItemRead


def get_item(
    db: Session,
    item_id: int,
    *,
    query_filter: ItemQueryFilter | None = None,
    client_id: int | None = None,
) -> ItemRead:
    """Get item by id."""

    # default empty query filter
    query_filter = query_filter or ItemQueryFilter()

    # no client id
    if client_id is None:
        return _get_item_without_client_specific_fields(
            db=db,
            item_id=item_id,
            query_filter=query_filter,
        )

    # with client id
    return _get_item_with_client_specific_fields(
        db=db,
        item_id=item_id,
        query_filter=query_filter,
        client_id=client_id,
    )


def _get_item_without_client_specific_fields(
    db: Session,
    item_id: int,
    *,
    query_filter: ItemQueryFilter,
) -> ItemRead:
    """Get item tuned without client-specific fields."""

    stmt = select(Item).where(Item.id == item_id)

    # apply filtering
    stmt = query_filter.apply(stmt)

    try:
        item = db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": item_id}
        raise ItemNotFoundError(key) from error

    return ItemRead.model_validate(item)


def _get_item_with_client_specific_fields(
    db: Session,
    item_id: int,
    *,
    query_filter: ItemQueryFilter,
    client_id: int,
) -> ItemRead:
    """Get item tuned with client-specific fields."""

    stmt = (
        select(Item, ItemLike.id, ItemSave.id)
        .outerjoin(
            ItemLike, and_(ItemLike.item_id == Item.id, ItemLike.user_id == client_id)
        )
        .outerjoin(
            ItemSave, and_(ItemSave.item_id == Item.id, ItemSave.user_id == client_id)
        )
        .where(Item.id == item_id)
    )

    # apply filtering
    stmt = query_filter.apply(stmt)

    try:
        item, like_id, save_id = db.execute(stmt).unique().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": item_id}
        raise ItemNotFoundError(key) from error

    return ItemRead.model_validate(
        {
            **ItemRead.model_validate(item).model_dump(),
            "owned": item.owner_id == client_id,
            "liked": like_id is not None,
            "saved": save_id is not None,
        }
    )
