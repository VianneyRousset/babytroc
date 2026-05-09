import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.email_report import send_report_email
from app.domains.report.enums import ReportType
from app.domains.report.models import Report
from app.domains.chat.schemas.base import ChatId
from app.domains.chat.schemas.query import ChatMessageReadQueryFilter, ChatReadQueryFilter
from app.domains.report.schemas.create import ReportCreate
from app.domains.chat.services.chat.read import get_chat
from app.domains.chat.services.message.read import list_messages
from app.domains.user.services.read import get_user_private


async def report_chat(
    db: AsyncSession,
    chat_id: ChatId,
    *,
    query_filter: ChatReadQueryFilter | None = None,
    reported_by_user_id: int,
    report_create: ReportCreate,
    email_client=None,
    app_name: str = "",
    moderator_email: str = "",
):
    """Create a report for the chat with `chat_id`.

    Snapshots all messages, members, and item info so evidence
    is preserved even if messages are later deleted or modified.
    """

    # fetch chat (raises ChatNotFoundError if missing / not member)
    chat = await get_chat(
        db=db,
        chat_id=chat_id,
        query_filter=query_filter,
    )

    # fetch all messages in the chat
    messages_result = await list_messages(
        db=db,
        query_filter=ChatMessageReadQueryFilter(
            chat_id=chat_id,
            member_id=reported_by_user_id,
        ),
    )
    messages = messages_result.data

    # fetch reporter name
    reporter = await get_user_private(db=db, user_id=reported_by_user_id)

    # snapshot chat state
    saved_info = json.dumps(
        {
            "chat_id": str(chat.id),
            "item": {
                "id": chat.item.id,
                "name": chat.item.name,
            },
            "owner": {
                "id": chat.owner.id,
                "name": chat.owner.name,
            },
            "borrower": {
                "id": chat.borrower.id,
                "name": chat.borrower.name,
            },
            "messages": [
                {
                    "id": msg.id,
                    "sender_id": msg.sender_id,
                    "text": msg.text,
                    "message_type": msg.message_type.name,
                    "creation_date": str(msg.creation_date),
                    "seen": msg.seen,
                }
                for msg in messages
            ],
        },
        ensure_ascii=False,
    )

    # create report
    report = Report(
        description=report_create.message,
        report_type=ReportType.chat,
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
            report_type=ReportType.chat,
            reporter_name=reporter.name,
            description=report_create.message,
            context=report_create.context,
            saved_info=saved_info,
        )
