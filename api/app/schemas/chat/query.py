from typing import Optional

from sqlalchemy import Select

from app.models.chat import Chat, ChatMessage
from app.models.item import Item
from app.schemas.base import QueryFilterBase
from app.schemas.chat.base import ChatId


class ChatQueryFilter(QueryFilterBase):
    """Filter of the chat query."""

    item_id: Optional[int] = None
    borrower_id: Optional[int] = None
    owner_id: Optional[int] = None
    member_id: Optional[int] = None

    def apply(self, stmt: Select) -> Select:
        """Apply filtering."""

        # filter item_id
        if self.item_id is not None:
            stmt = stmt.where(Chat.item_id == self.item_id)

        # filter borrower_id
        if self.borrower_id is not None:
            stmt = stmt.where(Chat.borrower_id == self.borrower_id)

        # filter owner_id
        if self.owner_id is not None:
            stmt = stmt.join(Item)
            stmt = stmt.where(Item.owner_id == self.owner_id)

        # filter member_id
        if self.member_id is not None:
            stmt = stmt.join(Item)
            stmt = stmt.where(
                (Chat.borrower_id == self.member_id) | (Item.owner_id == self.member_id)
            )

        return stmt


class ChatMessageQueryFilter(QueryFilterBase):
    """Filter of the chat message query."""

    chat_id: Optional[ChatId] = None
    item_id: Optional[int] = None
    borrower_id: Optional[int] = None
    owner_id: Optional[int] = None
    sender_id: Optional[int] = None
    member_id: Optional[int] = None

    seen: Optional[bool] = None

    def apply(self, stmt: Select) -> Select:
        """Apply filtering."""

        # filter chat_id
        if self.chat_id is not None:
            stmt = stmt.join(Chat)
            stmt = stmt.where(
                (Chat.item_id == self.chat_id.item_id)
                & (Chat.borrower_id == self.chat_id.borrower_id)
            )

        # filter item_id
        if self.item_id is not None:
            stmt = stmt.join(Chat)
            stmt = stmt.where(Chat.item_id == self.item_id)

        # filter borrower_id
        if self.borrower_id is not None:
            stmt = stmt.join(Chat)
            stmt = stmt.where(Chat.borrower_id == self.borrower_id)

        # filter owner_id
        if self.borrower_id is not None:
            stmt = stmt.join(Chat)
            stmt = stmt.join(Item)
            stmt = stmt.where(Item.owner_id == self.owner_id)

        # filter sender_id
        if self.sender_id is not None:
            stmt = stmt.where(ChatMessage.sender_id == self.sender_id)

        # filter member_id
        if self.member_id is not None:
            stmt = stmt.join(Chat)
            stmt = stmt.join(Item)
            stmt = stmt.where(
                (Chat.borrower_id == self.member_id) | (Item.owner_id == self.member_id)
            )

        # filter seen
        if self.seen is not None:
            stmt = stmt.where(ChatMessage.seen == self.seen)

        return stmt
