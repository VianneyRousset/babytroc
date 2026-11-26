import json

from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.item.services.read import get_item
from babytroc.domains.moderation.enums import ModerationReportType
from babytroc.domains.moderation.events import ModerationReportCreated
from babytroc.domains.moderation.models import ModerationReport
from babytroc.domains.moderation.schemas.create import ModerationReportCreate
from babytroc.infrastructure.events import emit


async def report_item(
    db: AsyncSession,
    item_id: int,
    reported_by_user_id: int,
    report_create: ModerationReportCreate,
    *,
    email_client=None,
    app_name: str = "",
    moderator_email: str = "",
) -> None:
    """Create a report for the item with `item_id`.

    Snapshots the item's current state so evidence is preserved
    even if the item is later modified.
    """

    # fetch item (raises ItemNotFoundError if missing)
    item = await get_item(db=db, item_id=item_id)

    # snapshot item state
    saved_info = json.dumps(
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "targeted_age_months": str(item.targeted_age_months),
            "owner": {
                "id": item.owner.id,
                "name": item.owner.name,
            },
            "region_ids": sorted(item.region_ids),
            "image_names": item.image_names,
            "available": item.available,
            "likes_count": item.likes_count,
        },
        ensure_ascii=False,
    )

    # create report
    report = ModerationReport(
        description=report_create.message,
        report_type=ModerationReportType.item,
        created_by=reported_by_user_id,
        saved_info=saved_info,
        context=report_create.context,
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)

    await emit(db, ModerationReportCreated.from_report(report))
