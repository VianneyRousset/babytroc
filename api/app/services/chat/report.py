from sqlalchemy.orm import Session

from app.clients import database
from app.enums import ReportType
from app.schemas.chat import (
    ChatListRead,
    ChatMessageRead,
    ChatRead,
    ReportCreate,
)


def report_user_chat(
    db: Session,
    user_id: int,
    chat_id: int,
    reported_by_user_id: int,
    report_create: ReportCreate,
):
    """Create a report for the chat with `chat_id`.

    Info about the chat is saved as well as the given client provided description and
    context.

    The chat must have `user_id` as participant.
    """

    chat = database.chat.get_chat_for_report(
        chat_id=chat_id,
        user_id=user_id,
    )

    database.report.insert_report(
        report_type=ReportType.chat,
        reported_by_user_id=reported_by_user_id,
        saved_info=chat.json(),
        description=report_create.description,
        context=report_create.context,
    )

    # TODO send an email to moderators
