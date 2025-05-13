from sqlalchemy.orm import Session

from app.schemas.report.create import ReportCreate


def report_user(
    db: Session,
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
