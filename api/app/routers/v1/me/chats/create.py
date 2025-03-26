from typing import Annotated

from fastapi import Body, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.chat.base import ChatId
from app.schemas.chat.create import ChatMessageCreate
from app.schemas.chat.read import ChatMessageRead

from .annotations import chat_id_annotation
from .router import router


@router.post(
    "/{chat_id}/messages",
    status_code=status.HTTP_200_OK,
)
def send_message_to_chat(
    request: Request,
    chat_id: chat_id_annotation,
    chat_message_create: Annotated[
        ChatMessageCreate,
        Body(),
    ],
    db: Annotated[Session, Depends(get_db_session)],
) -> ChatMessageRead:
    """Send message to chat."""

    client_user_id = services.auth.check_auth(request)

    return services.chat.send_message_text(
        db=db,
        chat_id=ChatId.from_str(chat_id),
        sender_id=client_user_id,
        text=chat_message_create.text,
    )
