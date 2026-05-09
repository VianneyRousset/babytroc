import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.report.enums import ReportType
from app.domains.report.models import Report
from app.domains.report.schemas.create import ReportCreate
from app.domains.user.services.read import get_user_private
from app.infrastructure.email_report import send_report_email


async def report_user(
    db: AsyncSession,
    user_id: int,
    reported_by_user_id: int,
    report_create: ReportCreate,
    *,
    email_client=None,
    app_name: str = "",
    moderator_email: str = "",
) -> None:
    """Create a report for the user with `user_id`.

    Snapshots the user's current state so evidence is preserved
    even if the user later modifies their profile.
    """

    # fetch user (raises UserNotFoundError if missing)
    user = await get_user_private(db=db, user_id=user_id)

    # fetch reporter name
    reporter = await get_user_private(db=db, user_id=reported_by_user_id)

    # snapshot user state
    saved_info = json.dumps(
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar_seed": user.avatar_seed,
            "stars_count": user.stars_count,
            "items_count": user.items_count,
            "likes_count": user.likes_count,
            "validated": user.validated,
        },
        ensure_ascii=False,
    )

    # create report
    report = Report(
        description=report_create.message,
        report_type=ReportType.user,
        created_by=reported_by_user_id,
        saved_info=saved_info,
        context=report_create.context,
    )
    db.add(report)

    # send email to moderators
    if email_client and moderator_email:
        await send_report_email(
            email_client,
            app_name=app_name,
            moderator_email=moderator_email,
            report_type=ReportType.user,
            reporter_name=reporter.name,
            description=report_create.message,
            context=report_create.context,
            saved_info=saved_info,
        )
