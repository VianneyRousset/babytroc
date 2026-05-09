from typing import Annotated

from fastapi import Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.chat import services as chat_services
from app.domains.chat.schemas.base import ChatId
from app.domains.chat.schemas.query import ChatReadQueryFilter
from app.domains.report.schemas.create import ReportCreate
from app.infrastructure.database import get_db_session
from app.routers.v1.auth import client_id_annotation

from .annotations import chat_id_annotation
from .router import router


@router.post(
    "/{chat_id}/report",
    status_code=status.HTTP_201_CREATED,
)
async def report_client_chat(
    client_id: client_id_annotation,
    chat_id: chat_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report fields."),
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """Report client's chat by id."""

    parsed_chat_id = ChatId.model_validate(chat_id)

    return await chat_services.report_chat(
        db=db,
        chat_id=parsed_chat_id,
        query_filter=ChatReadQueryFilter(member_id=client_id),
        reported_by_user_id=client_id,
        report_create=report_create,
    )
