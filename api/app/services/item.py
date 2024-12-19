from typing import Optional

from sqlalchemy.orm import Session

from app import domain
from app.clients import database
from app.enums import ReportType
from app.models.item import Item
from app.schemas.item.create import ItemCreate
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.private import ItemPrivateRead
from app.schemas.item.read import ItemRead
from app.schemas.item.update import ItemUpdate
from app.schemas.report import ReportCreate


async def create_item(
    db: Session,
    owner_id: int,
    item_create: ItemCreate,
) -> ItemPreviewRead:
    """Create a new item in the database."""

    # TODO index data in search engine
    item = await database.item.create_item(
        db=db,
        name=item_create.name,
        description=item_create.description,
        regions=item_create.regions,
        owner_id=owner_id,
        images=item_create.images,
        targeted_age_months=item_create.targeted_age_months,
        blocked=item_create.blocked,
        load_attributes=[Item.images],
    )

    await database.user.add_stars_to_user(
        db=db,
        user_id=owner_id,
        added_stars_count=domain.star.get_stars_gain_when_adding_item(1),
    )

    return ItemPreviewRead.from_orm(item)


async def list_items(
    db: Session,
    terms: Optional[list[str]] = None,
    create_before_item_id: Optional[int] = None,
    count: Optional[int] = 64,
    targeted_age_months: Optional[list[int]] = None,
    regions: Optional[list[int]] = None,
    owner_id: Optional[int] = None,
) -> list[ItemPreviewRead]:
    """List items matchings criteria in the database.

    If the list of strings `terms` is provided, those strings are used to filter the
    items based on their name and description. All the terms has to be present in the
    name or the description of the item to be returned.

    If `create_before_item_id` is provided, only items created before that item id will
    be returned.

    If `count` is provided, the number of returned items is limited to `count`.

    If `targeted_age_months` is provided, items with `targeted_age_months` range must overlap the
    given range to be returned.

    If `regions` is provided, items must be in one of those regions to
    be returned.

    If `owner_id` is provided, item must be owned by the user with this ID to be
    returned.
    """

    # search in db
    # TODO use quickwit or elasticsearch here
    items = await database.item.list_items(
        db=db,
        terms=terms,
        created_before_item_id=create_before_item_id,
        count=count,
        targeted_age_months=targeted_age_months,
        regions=regions,
        load_attributes=[Item.images],
    )

    return [ItemPreviewRead.from_orm(item) for item in items]


async def get_item(
    db: Session,
    item_id: int,
) -> ItemRead:
    """Get item by id."""

    # get item from databse
    # TODO replace client concept with a non-client concept
    item = await database.item.get_item(
        db=db,
        item_id=item_id,
        load_attributes=[
            Item.owner,
            Item.images,
            Item.regions,
            Item.likes_count,
        ],
    )

    return ItemRead.from_orm(item)


async def get_private_item(
    db: Session,
    item_id: int,
    owner_id: Optional[int] = None,
) -> ItemPrivateRead:
    """Get item by id.

    If `owner_id` is provided, the item must be owned by the user with this ID.
    """

    # get item from databse
    # TODO replace client concept with a non-client concept
    item = await database.item.get_item(
        db=db,
        item_id=item_id,
        owner_id=owner_id,
        load_attributes=[
            Item.owner,
            Item.images,
            Item.regions,
            Item.likes_count,
            Item.loans,
            Item.active_loans,
        ],
    )

    return ItemPrivateRead.from_orm(item)


async def update_item(
    db: Session,
    *,
    item_id: int,
    item_update: ItemUpdate,
    owner_id: Optional[int] = None,
) -> ItemPrivateRead:
    """Update item owned by `owner_id`."""

    # TODO check if images exists

    item = await database.item.update_item(
        db=db,
        item_id=item_id,
        owner_id=owner_id,
        attributes=item_update.dict(exclude_none=True),
        load_attributes=[
            Item.owner,
            Item.images,
            Item.regions,
            Item.likes_count,
            Item.loans,
            Item.active_loans,
        ],
    )

    return ItemPrivateRead.from_orm(item)


async def delete_item(
    db: Session,
    item_id: int,
    owner_id: Optional[int] = None,
):
    """Delete the item with ID `item_id`.

    If `owner_id` is provided, the item must be owned by the user with this ID.
    """

    await database.item.delete_item(
        db=db,
        owner_id=owner_id,
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
