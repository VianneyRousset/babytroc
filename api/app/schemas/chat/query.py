from typing import Annotated

from pydantic import AliasChoices, Field
from sqlalchemy import Select

from app.models.chat import Chat, ChatMessage
from app.models.item import Item
from app.schemas.base import QueryFilterBase
from app.schemas.chat.base import ChatId
from app.schemas.query import QueryPageCursor


class ChatQueryFilter(QueryFilterBase):
    """Filter of the chat query."""

    item_id: int | None = None
    borrower_id: int | None = None
    owner_id: int | None = None
    member_id: int | None = None

    def apply(self, stmt: Select) -> Select:
        """Apply filtering."""

        if self.owner_id is not None or self.member_id is not None:
            stmt = stmt.join(Item)

        # filter item_id
        if self.item_id is not None:
            stmt = stmt.where(Chat.item_id == self.item_id)

        # filter borrower_id
        if self.borrower_id is not None:
            stmt = stmt.where(Chat.borrower_id == self.borrower_id)

        # filter owner_id
        if self.owner_id is not None:
            stmt = stmt.where(Item.owner_id == self.owner_id)

        # filter member_id
        if self.member_id is not None:
            stmt = stmt.where(
                (Chat.borrower_id == self.member_id) | (Item.owner_id == self.member_id)
            )

        return stmt


class ChatMessageQueryFilter(QueryFilterBase):
    """Filter of the chat message query."""

    chat_id: ChatId | None = None
    item_id: int | None = None
    borrower_id: int | None = None
    owner_id: int | None = None
    sender_id: int | None = None
    sender_id_not: int | None = None
    member_id: int | None = None

    seen: bool | None = None

    def apply(self, stmt: Select) -> Select:  # noqa: C901
        """Apply filtering."""

        if (
            self.chat_id is not None
            or self.item_id is not None
            or self.borrower_id is not None
            or self.owner_id is not None
            or self.member_id is not None
        ):
            stmt = stmt.join(Chat)

        if self.owner_id is not None or self.member_id:
            stmt = stmt.join(Item)

        # filter chat_id
        if self.chat_id is not None:
            stmt = stmt.where(
                (Chat.item_id == self.chat_id.item_id)
                & (Chat.borrower_id == self.chat_id.borrower_id)
            )

        # filter item_id
        if self.item_id is not None:
            stmt = stmt.where(Chat.item_id == self.item_id)

        # filter borrower_id
        if self.borrower_id is not None:
            stmt = stmt.where(Chat.borrower_id == self.borrower_id)

        # filter owner_id
        if self.owner_id is not None:
            stmt = stmt.where(Item.owner_id == self.owner_id)

        # filter sender_id
        if self.sender_id is not None:
            stmt = stmt.where(ChatMessage.sender_id == self.sender_id)

        # filter sender_id_not
        if self.sender_id_not is not None:
            stmt = stmt.where(ChatMessage.sender_id != self.sender_id_not)

        # filter member_id
        if self.member_id is not None:
            stmt = stmt.where(
                (Chat.borrower_id == self.member_id) | (Item.owner_id == self.member_id)
            )

        # filter seen
        if self.seen is not None:
            stmt = stmt.where(ChatMessage.seen == self.seen)

        return stmt


class ChatQueryPageCursor(QueryPageCursor):
    last_message_id: Annotated[
        int | None,
        Field(
            validation_alias=AliasChoices("last_message_id", "clmid"),
            serialization_alias="clmid",
        ),
    ] = None


class ChatMessageQueryPageCursor(QueryPageCursor):
    message_id: Annotated[
        int | None,
        Field(
            validation_alias=AliasChoices("message_id", "mid"),
            serialization_alias="mid",
        ),
    ] = None
