from datetime import datetime

from app.enums import ChatMessageType

from .base import Base
from .user import UserPreviewRead


class ChatBase(Base):
    pass


class ChatListRead(ChatBase):
    chats: list["ChatRead"]
    unseen_messages: list["ChatMessageRead"]


class ChatRead(ChatBase):
    id: int
    borrower: UserPreviewRead
    client_id: int


class ChatMessageRead(ChatBase):
    id: int
    message_type: ChatMessageType
    sender_id: int
    receiver_id: int
    creation_date: datetime
    seen: bool
    payload: str
