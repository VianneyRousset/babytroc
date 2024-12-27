from datetime import datetime
from typing import Optional

from app import models
from app.enums import ChatMessageType
from app.schemas.base import ReadBase
from app.schemas.user.preview import UserPreviewRead

from .base import ChatBase


class ChatRead(ChatBase, ReadBase):
    id: int
    borrower: UserPreviewRead
    client_id: int


class ChatMessageRead(ChatBase, ReadBase):
    id: int
    chat_id: str
    message_type: ChatMessageType
    sender_id: Optional[int]
    creation_date: datetime
    seen: bool
    payload: Optional[str]

    @classmethod
    def from_orm(cls, message: models.chat.ChatMessage):
        return cls(
            id=message.id,
            chat_id=f"{message.item_id}-{message.borrower_id}",
            message_type=message.message_type,
            sender_id=message.sender_id,
            creation_date=message.creation_date,
            seen=message.seen,
            payload=message.payload,
        )
