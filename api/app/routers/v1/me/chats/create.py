from typing import Annotated

from fastapi import Body, Depends, Request, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.chat.base import ChatId
from app.schemas.chat.create import ChatMessageCreate
from app.schemas.chat.read import ChatMessageRead
from app.schemas.chat.send import SendChatMessageText

from .annotations import chat_id_annotation
from .router import router


@router.post(
    "/{chat_id}/messages",
    status_code=status.HTTP_200_OK,
)
def send_message_to_chat(
    client_id: client_id_annotation,
    request: Request,
    chat_id: chat_id_annotation,
    chat_message_create: Annotated[
        ChatMessageCreate,
        Body(),
    ],
    db: Annotated[Session, Depends(get_db_session)],
) -> ChatMessageRead:
    """Send message to chat."""

    parsed_chat_id = ChatId.model_validate(chat_id)

    return services.chat.send_chat_message(
        db=db,
        message=SendChatMessageText(
            chat_id=parsed_chat_id,
            sender_id=client_id,
            text=chat_message_create.text,
        ),
    )
