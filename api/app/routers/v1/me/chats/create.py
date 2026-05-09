from typing import Annotated

from fastapi import Body, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.chat import services as chat_services
from app.domains.chat.schemas.base import ChatId
from app.domains.chat.schemas.create import ChatMessageCreate
from app.domains.chat.schemas.read import ChatMessageRead
from app.domains.chat.schemas.send import SendChatMessageText
from app.infrastructure.database import get_db_session
from app.routers.v1.auth import client_id_annotation

from .annotations import chat_id_annotation
from .router import router


@router.post(
    "/{chat_id}/messages",
    status_code=status.HTTP_200_OK,
)
async def send_message_to_chat(
    client_id: client_id_annotation,
    request: Request,
    chat_id: chat_id_annotation,
    chat_message_create: Annotated[
        ChatMessageCreate,
        Body(),
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ChatMessageRead:
    """Send message to chat."""

    parsed_chat_id = ChatId.model_validate(chat_id)

    return await chat_services.send_chat_message(
        db=db,
        message=SendChatMessageText(
            chat_id=parsed_chat_id,
            sender_id=client_id,
            text=chat_message_create.text,
        ),
    )
