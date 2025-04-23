from typing import Annotated

from fastapi import Body, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.chat.base import ChatId
from app.schemas.chat.read import ChatRead
from app.schemas.report.create import ReportCreate

from .annotations import chat_id_annotation
from .router import router


@router.post(
    "/{chat_id}/report",
    status_code=status.HTTP_201_CREATED,
)
def report_client_chat(
    client_id: client_id_annotation,
    chat_id: chat_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report fields."),
    ],
    db: Annotated[Session, Depends(get_db_session)],
) -> ChatRead:
    """Report client's chat by id."""

    return services.chat.report_chat(
        db=db,
        chat_id=ChatId.from_str(chat_id),
        reported_by_user_id=client_id,
        report_create=report_create,
    )
