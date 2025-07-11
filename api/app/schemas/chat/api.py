from typing import Annotated

from app.schemas.base import ApiQueryBase, FieldWithAlias, PageLimitField
from app.schemas.query import QueryPageOptions

from .query import (
    ChatMessageQueryFilter,
    ChatMessageQueryPageCursor,
    ChatQueryFilter,
    ChatQueryPageCursor,
)


class ChatApiQuery(ApiQueryBase, ChatQueryPageCursor):
    # limit
    limit: Annotated[int, PageLimitField()] = 32

    @property
    def chat_query_filter(self) -> ChatQueryFilter:
        return ChatQueryFilter()

    @property
    def chat_query_page_cursor(self) -> ChatQueryPageCursor:
        return ChatQueryPageCursor(
            last_message_id=self.last_message_id,
        )

    @property
    def chat_query_page_options(
        self,
    ) -> QueryPageOptions[ChatQueryPageCursor]:
        return QueryPageOptions[ChatQueryPageCursor](
            limit=self.limit,
            cursor=self.chat_query_page_cursor,
        )


class ChatMessageApiQuery(ApiQueryBase, ChatMessageQueryPageCursor):
    # seen
    seen: bool | None = FieldWithAlias(
        name="seen",
        alias="s",
        title="Seen messages",
        description=("Only select messages that have been seen."),
        examples=[True, False],
        default=None,
    )

    # limit
    limit: Annotated[int, PageLimitField()] = 32

    @property
    def chat_message_query_filter(self) -> ChatMessageQueryFilter:
        return ChatMessageQueryFilter(
            seen=self.seen,
        )

    @property
    def chat_message_query_page_cursor(self) -> ChatMessageQueryPageCursor:
        return ChatMessageQueryPageCursor(
            message_id=self.message_id,
        )

    @property
    def chat_message_query_page_options(
        self,
    ) -> QueryPageOptions[ChatMessageQueryPageCursor]:
        return QueryPageOptions[ChatMessageQueryPageCursor](
            limit=self.limit,
            cursor=self.chat_message_query_page_cursor,
        )
