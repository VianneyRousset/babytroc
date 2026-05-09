import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.email_report import send_report_email
from app.domains.report.enums import ReportType
from app.domains.report.models import Report
from app.domains.report.schemas.create import ReportCreate
from app.domains.item.services.read import get_item
from app.domains.user.services.read import get_user_private


async def report_item(
    db: AsyncSession,
    item_id: int,
    reported_by_user_id: int,
    report_create: ReportCreate,
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

    # fetch reporter name
    reporter = await get_user_private(db=db, user_id=reported_by_user_id)

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
    report = Report(
        description=report_create.message,
        report_type=ReportType.item,
        created_by=reported_by_user_id,
        saved_info=saved_info,
        context=report_create.context,
    )
    db.add(report)

    # send email
    if email_client and moderator_email:
        await send_report_email(
            email_client,
            app_name=app_name,
            moderator_email=moderator_email,
            report_type=ReportType.item,
            reporter_name=reporter.name,
            description=report_create.message,
            context=report_create.context,
            saved_info=saved_info,
        )
