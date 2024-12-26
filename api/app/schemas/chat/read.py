from datetime import datetime

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
    message_type: ChatMessageType
    sender_id: int
    receiver_id: int
    creation_date: datetime
    seen: bool
    payload: str

    @classmethod
    def from_orm(cls, message: models.chat.ChatMessage):
        return cls.model_validate(message)


class ChatListRead(ChatBase, ReadBase):
    chats: list[ChatRead]
    unseen_messages: list[ChatMessageRead]
