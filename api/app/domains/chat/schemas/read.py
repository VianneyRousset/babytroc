from datetime import datetime

from app.domains.chat.enums import ChatMessageType
from app.shared.schemas import ReadBase
from app.domains.item.schemas.preview import ItemPreviewRead
from app.domains.user.schemas.preview import UserPreviewRead

from .base import ChatBase, ChatId


class ChatRead(ChatBase, ReadBase):
    id: ChatId
    borrower: UserPreviewRead
    owner: UserPreviewRead
    item: ItemPreviewRead
    last_message_id: int | None


class ChatMessageRead(ChatBase, ReadBase):
    id: int
    chat_id: ChatId
    message_type: ChatMessageType
    sender_id: int | None
    creation_date: datetime
    seen: bool
    text: str | None
    loan_request_id: int | None
    loan_id: int | None
    item_id: int
    borrower_id: int
