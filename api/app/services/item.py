from typing import Optional

from sqlalchemy.orm import Session

from app import domain
from app.client import database
from app.enums import ReportType
from app.schemas.item import ItemCreate, ItemPreviewRead, ItemRead, ItemUpdate
from app.schemas.report import ReportCreate


async def create_item(
    db: Session,
    owner_user_id: int,
    item_create: ItemCreate,
) -> ItemPreviewRead:
    """Create a new item in the database."""

    item = await database.item.insert_item(
        db=db,
        owner_id=owner_user_id,
        name=item_create.name,
        description=item_create.description,
        images=item_create.images,
        targeted_age=item_create.targeted_age,
        regions=item_create.regions,
        blocked=item_create.regions,
    )

    return ItemPreviewRead.model_validate(item)


async def list_items(
    db: Session,
    terms: Optional[list[str]],
    create_before_item_id: Optional[int] = None,
    count: Optional[int] = 64,
    targeted_age: Optional[list[int]] = None,
    regions: Optional[list[int]] = None,
) -> list[ItemPreviewRead]:
    """List items matchings criteria in the database.

    If the list of strings `terms` is provided, those strings are used to filter the
    items based on their name and description. All the terms has to be present in the
    name or the description of the item to be returned.

    If `create_before_item_id` is provided, only items created before that item id will
    be returned.

    If `count` is provided, the number of returned items is limited to `count`.

    If `targeted_age` is provided, items with `targeted_age` range must overlap the
    given range to be returned.

    If the list of int `regions` is provided, items must be in one of those regions to
    be returned.
    """

    # search in db
    items = await database.item.search_items(
        db=db,
        terms=terms,
        create_before_item_id=create_before_item_id,
        count=count,
        targeted_age=targeted_age,
        regions=regions,
    )

    for item in items:
        # replace images by a list of image str ids (image urls)
        item.images = [img.id for img in item.images]

    return [ItemPreviewRead.model_validate(item) for item in items]


async def get_item_by_id_for_client(
    db: Session,
    item_id: int,
    client_user_id: int,
) -> ItemRead:
    """Get item by id tuned for the given client user id.

    In addition to the basic item fields such as name, description, images, etc,
    the information about wether the item is liked, bookmarked and/or borrowed by the
    client is given. If the client is the owner of the item, the list of loans as well
    as the blocked status are given.
    """

    # get item from databse
    # TODO replace client concept with a non-client concept
    item = await database.item.get_item_by_id_for_client(
        db=db,
        item_id=item_id,
        client_user_id=client_user_id,
    )

    # replace images by a list of image str ids (image urls)
    item.images = [img.id for img in item.images]

    # compute if the item is available
    item.available = domain.is_item_available(
        blocked=item.blocked,
        last_loan=item.loans,
    )

    # hide some infos if the client is not the owner of the item
    if item.owner.id != client_user_id:
        item.loans = None
        item.blocked = None

    return ItemRead.model_validate(item)


async def get_user_item_by_id_for_client(
    db: Session,
    item_id: int,
    owner_user_id: int,
    client_user_id: int,
) -> ItemRead:
    """Get item by id tuned for the given client user id.

    In addition to the basic item fields such as name, description, images, etc,
    the information about wether the item is liked, bookmarked and/or borrowed by the
    client is given. If the client is the owner of the item, the list of loans as well
    as the blocked status are given.

    The item must be owned by user with `owner_user_id`.
    """

    # get item from databse
    # TODO replace client concept with a non-client concept
    item = await database.item.get_item_by_id_for_client(
        db=db,
        item_id=item_id,
        owner_id=owner_user_id,
        client_user_id=client_user_id,
    )

    # replace images by a list of image str ids (image urls)
    item.images = [img.id for img in item.images]

    # compute if the item is available
    item.available = domain.is_item_available(
        blocked=item.blocked,
        last_loan=item.loans,
    )

    # hide some infos if the client is not the owner of the item
    if item.owner.id != client_user_id:
        item.loans = None
        item.blocked = None

    return ItemRead.model_validate(item)


async def list_user_items(
    db: Session,
    owner_user_id: int,
    create_before_item_id: int,
    count: int,
) -> list[ItemPreviewRead]:
    """List items ownned by user with `user_id`.

    If `create_before_item_id` is provided, only items created before that item id will
    be returned.

    If `count` is provided, the number of returned items is limited to `count`.
    """

    # search in db
    items = await database.item.search_items(
        db=db,
        owner_id=owner_user_id,
        create_before_item_id=create_before_item_id,
        count=count,
    )

    items = [ItemPreviewRead.model_validate(item) for item in items]

    return items


async def update_user_item(
    db: Session,
    owner_user_id: int,
    item_id: int,
    item_update: ItemUpdate,
) -> ItemPreviewRead:
    """Update item owned by `owner_user_id`."""

    item = await database.item.update_user_item(
        db=db,
        owner_id=owner_user_id,
        name=item_update.name,
        description=item_update.description,
        images=item_update.images,
        targeted_age=item_update.targeted_age,
        regions=item_update.regions,
        blocked=item_update.regions,
    )

    return ItemPreviewRead.model_validate(item)


async def delete_user_item(
    db: Session,
    owner_user_id: int,
    item_id: int,
):
    """Delete item owned by `owner_user_id`."""

    await database.item.delete_user_item(
        db=db,
        owner_id=owner_user_id,
        item_id=item_id,
    )


async def report_item(
    db: Session,
    item_id: int,
    reported_by_user_id: int,
    report_create: ReportCreate,
):
    """Create a report for the item with `item_id`.

    A maximum of item infos are saved as well as the given client provided description
    and context.
    """

    item = await database.item.get_item_for_report()

    await database.report.insert_report(
        report_type=ReportType.item,
        reported_by_user_id=reported_by_user_id,
        saved_info=item.json(),
        description=report_create.description,
        context=report_create.context,
    )

    # TODO send an email to moderators
