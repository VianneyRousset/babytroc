from typing import Annotated

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.chat import services as chat_services
from babytroc.domains.chat.schemas.base import ChatId
from babytroc.domains.chat.schemas.query import ChatMessageReadQueryFilter
from babytroc.domains.chat.schemas.read import ChatMessageRead
from babytroc.infrastructure.database import get_db_session
from babytroc.routers.v1.auth import client_id_annotation

from .annotations import chat_id_annotation, message_id_annotation
from .router import router


@router.post(
    "/{chat_id}/messages/{message_id}/see",
    status_code=status.HTTP_200_OK,
)
async def mark_client_chat_message_as_seen(
    client_id: client_id_annotation,
    chat_id: chat_id_annotation,
    message_id: message_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ChatMessageRead:
    """Mark client's chat message as seen."""

    parsed_chat_id = ChatId.model_validate(chat_id)

    return await chat_services.mark_message_as_seen(
        db=db,
        message_id=message_id,
        query_filter=ChatMessageReadQueryFilter(
            item_id=parsed_chat_id.item_id,
            borrower_id=parsed_chat_id.borrower_id,
            member_id=client_id,
            sender_id_not=client_id,
        ),
    )
