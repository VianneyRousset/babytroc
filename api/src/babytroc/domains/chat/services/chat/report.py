import json

from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.chat.schemas.base import ChatId
from babytroc.domains.chat.schemas.query import (
    ChatMessageReadQueryFilter,
    ChatReadQueryFilter,
)
from babytroc.domains.chat.services.chat.read import get_chat
from babytroc.domains.chat.services.message.read import list_messages
from babytroc.domains.moderation.enums import ModerationReportType
from babytroc.domains.moderation.events import ModerationReportCreated
from babytroc.domains.moderation.models import ModerationReport
from babytroc.domains.moderation.schemas.create import ModerationReportCreate
from babytroc.infrastructure.events import emit


async def report_chat(
    db: AsyncSession,
    chat_id: ChatId,
    *,
    query_filter: ChatReadQueryFilter | None = None,
    reported_by_user_id: int,
    report_create: ModerationReportCreate,
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
    report = ModerationReport(
        description=report_create.message,
        report_type=ModerationReportType.chat,
        created_by=reported_by_user_id,
        saved_info=saved_info,
        context=report_create.context,
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)

    await emit(db, ModerationReportCreated.from_report(report))
