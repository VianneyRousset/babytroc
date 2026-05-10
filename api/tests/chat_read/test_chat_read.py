from typing import Any

import pytest
from httpx import AsyncClient

from babytroc.domains.chat.schemas.read import ChatMessageRead, ChatRead
from babytroc.shared.pagination_utils import iter_chunks, iter_paginated_endpoint
from tests.utils import azip


class TestChatsRead:
    """Tests chats list read."""

    @pytest.mark.parametrize("count", [None, 16, 7])
    async def test_read_pages(
        self,
        count: int | None,
        alice_client: AsyncClient,
        alice_many_chats: list[ChatRead],
    ):
        """Read a check all pages of the chats."""

        assert len(alice_many_chats) > 70, "Poor data set"

        # check that chat last message ids are unique
        n_distinct_chats = len({chat.last_message_id for chat in alice_many_chats})
        n_chats = len(alice_many_chats)
        assert n_distinct_chats == n_chats

        # sort chats by last message id
        alice_many_chats = sorted(
            alice_many_chats,
            key=lambda chat: chat.last_message_id
            if chat.last_message_id is not None
            else -1,
            reverse=True,
        )

        params: dict[str, Any] = {
            **({"n": count} if count is not None else {}),
        }

        async for chats, expected_chats in azip(
            iter_paginated_endpoint(
                client=alice_client,
                url="/api/v1/me/chats",
                params=params,
            ),
            iter_chunks(
                alice_many_chats,
                count=count or 32,
                append_empty=True,
            ),
            strict=True,
        ):
            assert [ChatRead.model_validate(msg) for msg in chats] == expected_chats


class TestChatMessagesRead:
    """Tests chat messages list read."""

    @pytest.mark.parametrize("count", [None, 16, 7])
    async def test_read_pages(
        self,
        count: int | None,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        alice_many_messages_to_bob: list[ChatMessageRead],
    ):
        """Read a check all pages of the chat messages."""

        assert len(alice_many_messages_to_bob) > 70, "Poor data set"

        chat_id = alice_many_messages_to_bob[0].chat_id

        # sort messages
        alice_many_messages_to_bob = sorted(
            alice_many_messages_to_bob,
            key=lambda msg: msg.id,
            reverse=True,
        )

        params: dict[str, Any] = {
            **({"n": count} if count is not None else {}),
        }

        async for alice_messages, bob_messages, expected_messages in azip(
            iter_paginated_endpoint(
                client=alice_client,
                url=f"/api/v1/me/chats/{chat_id}/messages",
                params=params,
            ),
            iter_paginated_endpoint(
                client=bob_client,
                url=f"/api/v1/me/chats/{chat_id}/messages",
                params=params,
            ),
            iter_chunks(
                alice_many_messages_to_bob,
                count=count or 32,
                append_empty=True,
            ),
            strict=True,
        ):
            assert [
                ChatMessageRead.model_validate(msg) for msg in alice_messages
            ] == expected_messages
            assert [
                ChatMessageRead.model_validate(msg) for msg in bob_messages
            ] == expected_messages

    async def test_read_single_message(
        self,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        alice_many_messages_to_bob: list[ChatMessageRead],
    ):
        """Read a check all pages of the chat messages."""

        message = alice_many_messages_to_bob[0]
        chat_id = message.chat_id

        res = await alice_client.get(
            f"/api/v1/me/chats/{chat_id}/messages/{message.id}"
        )
        res.raise_for_status()

        read_message = ChatMessageRead.model_validate(res.json())

        assert read_message == message
