from fastapi import Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import database as db
from app import services
from app.schemas.chat.query import (
    ChatMessageQueryFilter,
)
from app.schemas.chat.read import ChatMessageRead

from .annotations import chat_id_annotation, chat_message_id_annotation
from .router import router


@router.post(
    "/{chat_id}/messages/{message_id}/see",
    status_code=status.HTTP_200_OK,
)
def mark_client_chat_message_as_seen(
    request: Request,
    chat_id: chat_id_annotation,
    message_id: chat_message_id_annotation,
    db: Session = Depends(db.get_db_session),
) -> ChatMessageRead:
    """Mark client's chat message as seen."""

    client_user_id = services.auth.check_auth(request)

    return services.chat.mark_user_chat_message_as_seen(
        db=db,
        chat_message_id=message_id,
        query_filter=ChatMessageQueryFilter(
            item_id=chat_id.item_id,
            borrower_id=chat_id.borrower_id,
            member_id=client_user_id,
        ),
    )
