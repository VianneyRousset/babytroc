from datetime import datetime
from typing import Optional

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


class ChatMessageRead(ChatBase, ReadBase):
    id: int
    chat_id: ChatId
    message_type: ChatMessageType
    sender_id: Optional[int]
    creation_date: datetime
    seen: bool
    text: Optional[str]
    loan_request_id: Optional[int]
    loan_id: Optional[int]
    item_id: int
    borrower_id: int
