from datetime import datetime
from typing import Generic, Optional

from sqlalchemy import Select

from app.models.chat import Chat, ChatMessage
from app.models.user import User
from app.models.item import Item
from app.schemas.base import (
    QueryFilterBase,
    QueryPageOptionsBase,
    QueryPageResultBase,
    ResultType,
)


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


class ChatQueryPageOptions(QueryPageOptionsBase):
    """Options on the queried page of chats."""

    limit: Optional[int] = None
    last_message_date_lt: Optional[datetime] = None

    def apply(self, stmt: Select) -> Select:
        # apply limit
        if self.limit is not None:
            stmt = stmt.limit(self.limit)

        # if loan_request_id_lt is provided, add it to the query
        if self.loan_request_id_lt is not None:
            stmt = stmt.where(Chat.id < self.loan_request_id_lt)

        return stmt


class ChatQueryPageResult(QueryPageResultBase, Generic[ResultType]):
    """Info on the result page of chats."""

    query_filter: ChatQueryFilter
    page_options: ChatQueryPageOptions


class ChatMessageQueryFilter(QueryFilterBase):
    """Filter of the chat message query."""

    chat_id: Optional[int] = None
    sender_id: Optional[int] = None
    borrower_id: Optional[int] = None
    member_id: Optional[int] = None
    seen: Optional[bool] = None

    def apply(self, stmt: Select) -> Select:
        """Apply filtering."""

        # filter chat_id
        if self.chat_id is not None:
            stmt = stmt.where(ChatMessage.chat_id == self.chat_id)

        # filter sender_id
        if self.sender_id is not None:
            stmt = stmt.where(ChatMessage.sender_id == self.sender_id)

        # filter borrower_id
        if self.borrower_id is not None:
            stmt = stmt.where(ChatMessage.borrower_id == self.borrower_id)

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


class ChatMessageQueryPageOptions(QueryPageOptionsBase):
    """Options on the queried page of messages."""

    limit: Optional[int] = None
    message_id_lt: Optional[int] = None

    def apply(self, stmt: Select) -> Select:
        # apply limit
        if self.limit is not None:
            stmt = stmt.limit(self.limit)

        # if loan_request_id_lt is provided, add it to the query
        if self.message_id_lt is not None:
            stmt = stmt.where(ChatMessage.id < self.loan_request_id_lt)

        return stmt


class ChatMessageQueryPageResult(QueryPageResultBase, Generic[ResultType]):
    """Info on the result page of messages."""

    query_filter: ChatMessageQueryFilter
    page_options: ChatMessageQueryPageOptions
