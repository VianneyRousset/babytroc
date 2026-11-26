from babytroc.domains.moderation.events import ModerationReportCreated
from babytroc.infrastructure.events import on


@on(ModerationReportCreated, critical=False)
async def send_emails_to_moderators_on_report_created(
    db,
    event: ModerationReportCreated,
):
    pass
