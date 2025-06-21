from sqlalchemy.orm import Session

from app.schemas.chat.query import ChatQueryFilter
from app.schemas.report.create import ReportCreate


def report_chat(
    db: Session,
    chat_id: int,
    *,
    query_filter: ChatQueryFilter | None = None,
    reported_by_user_id: int,
    report_create: ReportCreate,
):
    """Create a report for the chat with `chat_id`.

    Info about the chat is saved as well as the given client provided description and
    context.

    The chat must have `user_id` as member.
    """

    msg = "report_chat"
    raise NotImplementedError(msg)

    # TODO create report
    # TODO send an email to moderators
