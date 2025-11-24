from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chat.base import ChatId
from app.schemas.chat.query import ChatReadQueryFilter
from app.schemas.report.create import ReportCreate


async def report_chat(
    db: AsyncSession,
    chat_id: ChatId,
    *,
    query_filter: ChatReadQueryFilter | None = None,
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
