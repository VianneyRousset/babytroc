from typing import Annotated

from fastapi import Body, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import database as db
from app import services
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
    request: Request,
    chat_id: chat_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report fields."),
    ],
    db: Session = Depends(db.get_db_session),
) -> ChatRead:
    """Report client's chat by id."""

    client_user_id = services.auth.check_auth(request)

    return services.chat.report_user_chat(
        db=db,
        user_id=client_user_id,
        chat_id=ChatId.from_str(chat_id),
        reported_by_user_id=client_user_id,
        report_create=report_create,
    )
