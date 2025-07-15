from typing import Annotated

from fastapi import Depends, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.chat.base import ChatId
from app.schemas.chat.query import ChatMessageQueryFilter
from app.schemas.chat.read import ChatMessageRead

from .annotations import chat_id_annotation, message_id_annotation
from .router import router


@router.post(
    "/{chat_id}/messages/{message_id}/see",
    status_code=status.HTTP_200_OK,
)
def mark_client_chat_message_as_seen(
    client_id: client_id_annotation,
    chat_id: chat_id_annotation,
    message_id: message_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> ChatMessageRead:
    """Mark client's chat message as seen."""

    parsed_chat_id = ChatId.model_validate(chat_id)

    return services.chat.mark_message_as_seen(
        db=db,
        message_id=message_id,
        query_filter=ChatMessageQueryFilter(
            item_id=parsed_chat_id.item_id,
            borrower_id=parsed_chat_id.borrower_id,
            member_id=client_id,
            sender_id_not=client_id,
        ),
    )
