from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.report.create import ReportCreate


async def report_user(
    db: AsyncSession,
    user_id: int,
    reported_by_user_id: int,
    report_create: ReportCreate,
) -> None:
    """Create a report for the user with `user_id`.

    A maximum of info about the user is saved as well as the given client provided
    description and context.
    """

    # TODO get all info and create a report
    # TODO send an email to moderators
