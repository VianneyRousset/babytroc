from datetime import datetime
from typing import Optional

from pydantic import field_serializer

from app.enums import ChatMessageType
from app.schemas.base import ReadBase
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.user.preview import UserPreviewRead

from .base import ChatBase, ChatId


class ChatRead(ChatBase, ReadBase):
    id: ChatId
    borrower: UserPreviewRead
    owner: UserPreviewRead
    item: ItemPreviewRead
    last_message_id: int

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

    @field_serializer("chat_id")
    def serialize_dt(self, chat_id: ChatId, _info):
        return str(chat_id)
