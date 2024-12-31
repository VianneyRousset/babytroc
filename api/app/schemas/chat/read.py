from datetime import datetime
from typing import Optional

from pydantic import field_serializer

from app import models
from app.enums import ChatMessageType
from app.schemas.base import ReadBase
from app.schemas.user.preview import UserPreviewRead

from .base import ChatBase, ChatId


class ChatRead(ChatBase, ReadBase):
    id: ChatId
    borrower: UserPreviewRead

    @classmethod
    def from_orm(cls, chat: models.chat.Chat):
        return cls(
            id=ChatId(
                item_id=chat.item_id,
                borrower_id=chat.borrower_id,
            ),
            borrower=UserPreviewRead.from_orm(chat.borrower),
        )

    @field_serializer("id")
    def serialize_id(self, chat_id: ChatId, _info):
        return str(chat_id)


class ChatMessageRead(ChatBase, ReadBase):
    id: int
    chat_id: ChatId
    message_type: ChatMessageType
    sender_id: Optional[int]
    creation_date: datetime
    seen: bool
    payload: Optional[str]

    @classmethod
    def from_orm(cls, message: models.chat.ChatMessage):
        return cls(
            id=message.id,
            chat_id=ChatId(
                item_id=message.item_id,
                borrower_id=message.borrower_id,
            ),
            message_type=message.message_type,
            sender_id=message.sender_id,
            creation_date=message.creation_date,
            seen=message.seen,
            payload=message.payload,
        )

    @field_serializer("chat_id")
    def serialize_dt(self, chat_id: ChatId, _info):
        return str(chat_id)
