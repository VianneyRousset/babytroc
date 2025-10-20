from typing import Annotated

from sqlalchemy import Select

from app.models.chat import Chat, ChatMessage
from app.models.item import Item
from app.schemas.base import (
    DeleteQueryFilter,
    FieldWithAlias,
    Joins,
    QueryFilter,
    ReadQueryFilter,
    StatementT,
    UpdateQueryFilter,
)
from app.schemas.chat.base import ChatId
from app.schemas.query import QueryPageCursor


class ChatQueryFilterItem(QueryFilter):
    """Filter chats by item."""

    item_id: int | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(Chat.item_id == self.item_id)
            if self.item_id is not None
            else stmt
        )


class ChatQueryFilterBorrower(QueryFilter):
    """Filter chats by borrower."""

    borrower_id: int | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(Chat.borrower_id == self.borrower_id)
            if self.borrower_id is not None
            else stmt
        )


class ChatQueryFilterOwner(ReadQueryFilter):
    """Filter chats by owner."""

    owner_id: int | None = None

    @property
    def _joins(self) -> Joins:
        return super()._joins + ([Item] if self.owner_id is not None else [])

    def _filter_read(self, stmt: Select) -> Select:
        return super()._filter_read(
            stmt.where(Item.owner_id == self.owner_id)
            if self.owner_id is not None
            else stmt
        )


class ChatQueryFilterMember(ReadQueryFilter):
    """Filter chats by member."""

    member_id: int | None = None

    @property
    def _joins(self) -> Joins:
        return super()._joins + ([Item] if self.member_id is not None else [])

    def _filter_read(self, stmt: Select) -> Select:
        return super()._filter_read(
            stmt.where(
                (Chat.borrower_id == self.member_id) | (Item.owner_id == self.member_id)
            )
            if self.member_id is not None
            else stmt
        )


class ChatReadQueryFilter(
    ChatQueryFilterItem,
    ChatQueryFilterBorrower,
    ChatQueryFilterOwner,
    ChatQueryFilterMember,
    ReadQueryFilter,
):
    """Filter of the chat read query."""


class ChatUpdateQueryFilter(
    ChatQueryFilterItem,
    ChatQueryFilterBorrower,
    UpdateQueryFilter,
):
    """Filter of the chat update query."""


class ChatDeleteQueryFilter(
    ChatQueryFilterItem,
    ChatQueryFilterBorrower,
    DeleteQueryFilter,
):
    """Filter of the chat delete query."""


class ChatMessageQueryFilterChat(ReadQueryFilter):
    """Filter chat messages by chat."""

    chat_id: ChatId | None = None

    @property
    def _joins(self) -> Joins:
        return super()._joins + ([Chat] if self.chat_id is not None else [])

    def _filter_read(self, stmt: Select) -> Select:
        return super()._filter_read(
            stmt.where(
                (Chat.item_id == self.chat_id.item_id)
                & (Chat.borrower_id == self.chat_id.borrower_id)
            )
            if self.chat_id is not None
            else stmt
        )


class ChatMessageQueryFilterItem(ReadQueryFilter):
    """Filter chat messages by item."""

    item_id: int | None = None

    @property
    def _joins(self) -> Joins:
        return super()._joins + ([Chat] if self.item_id is not None else [])

    def _filter_read(self, stmt: Select) -> Select:
        return super()._filter_read(
            stmt.where(Chat.item_id == self.item_id)
            if self.item_id is not None
            else stmt
        )


class ChatMessageQueryFilterBorrower(ReadQueryFilter):
    """Filter chat messages by borrower."""

    borrower_id: int | None = None

    @property
    def _joins(self) -> Joins:
        return super()._joins + ([Chat] if self.borrower_id is not None else [])

    def _filter_read(self, stmt: Select) -> Select:
        return super()._filter_read(
            stmt.where(Chat.borrower_id == self.borrower_id)
            if self.borrower_id is not None
            else stmt
        )


class ChatMessageQueryFilterOwner(ReadQueryFilter):
    """Filter chat messages by owner."""

    owner_id: int | None = None

    @property
    def _joins(self) -> Joins:
        return super()._joins + ([Chat, Item] if self.owner_id is not None else [])

    def _filter_read(self, stmt: Select) -> Select:
        return super()._filter_read(
            stmt.where(Item.owner_id == self.owner_id)
            if self.owner_id is not None
            else stmt
        )


class ChatMessageQueryFilterSender(QueryFilter):
    """Filter chat messages by sender."""

    sender_id: int | None = None
    sender_id_not: int | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        # filter sender_id
        if self.sender_id is not None:
            stmt = stmt.where(ChatMessage.sender_id == self.sender_id)

        # filter sender_id_not
        if self.sender_id_not is not None:
            stmt = stmt.where(ChatMessage.sender_id != self.sender_id_not)

        return super()._filter(stmt)


class ChatMessageQueryFilterMember(ReadQueryFilter):
    """Filter chat messages by member."""

    member_id: int | None = None

    @property
    def _joins(self) -> Joins:
        return super()._joins + ([Chat, Item] if self.member_id is not None else [])

    def _filter_read(self, stmt: Select) -> Select:
        if self.member_id is None:
            return super()._filter_read(stmt)

        return super()._filter_read(
            stmt.where(
                (Chat.borrower_id == self.member_id) | (Item.owner_id == self.member_id)
            )
            if self.member_id is not None
            else stmt
        )


class ChatMessageQueryFilterSeen(QueryFilter):
    """Filter chat messages by seen status."""

    seen: bool | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(ChatMessage.seen == self.seen) if self.seen is not None else stmt
        )


class ChatMessageReadQueryFilter(
    ChatMessageQueryFilterSender,
    ChatMessageQueryFilterSeen,
    ChatMessageQueryFilterBorrower,
    ChatMessageQueryFilterItem,
    ChatMessageQueryFilterMember,
    ChatMessageQueryFilterOwner,
    ChatMessageQueryFilterChat,
    ReadQueryFilter,
):
    """Filter of the chat message read query."""


class ChatMessageUpdateQueryFilter(
    ChatMessageQueryFilterSender,
    ChatMessageQueryFilterSeen,
    UpdateQueryFilter,
):
    """Filter of the chat message update query."""


class ChatMessageDeleteQueryFilter(
    ChatMessageQueryFilterSender,
    ChatMessageQueryFilterSeen,
    DeleteQueryFilter,
):
    """Filter of the chat message update query."""


class ChatQueryPageCursor(QueryPageCursor):
    last_message_id: Annotated[
        int | None,
        FieldWithAlias(
            name="last_message_id",
            alias="clm",
        ),
    ] = None


class ChatMessageQueryPageCursor(QueryPageCursor):
    message_id: Annotated[
        int | None,
        FieldWithAlias(
            name="message_id",
            alias="cid",
        ),
    ] = None
