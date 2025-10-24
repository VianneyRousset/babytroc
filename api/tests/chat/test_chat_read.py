from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.schemas.chat.read import ChatMessageRead, ChatRead
from app.utils.pagination import iter_chunks, iter_paginated_endpoint


class TestChatsRead:
    """Tests chats list read."""

    @pytest.mark.parametrize("count", [None, 16, 7])
    def test_read_pages(
        self,
        count: int | None,
        alice_client: TestClient,
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
            key=lambda chat: chat.last_message_id,
            reverse=True,
        )

        params: dict[str, Any] = {
            **({"n": count} if count is not None else {}),
        }

        for alice_chats, expected_chats in zip(
            iter_paginated_endpoint(
                client=alice_client,
                url="/v1/me/chats",
                params=params,
            ),
            iter_chunks(
                alice_many_chats,
                count=count or 32,
                append_empty=True,
            ),
            strict=True,
        ):
            assert [
                ChatMessageRead.model_validate(msg) for msg in alice_chats
            ] == expected_chats


class TestChatMessagesRead:
    """Tests chat messages list read."""

    @pytest.mark.parametrize("count", [None, 16, 7])
    def test_read_pages(
        self,
        count: int | None,
        alice_client: TestClient,
        bob_client: TestClient,
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

        for alice_messages, bob_messages, expected_messages in zip(
            iter_paginated_endpoint(
                client=alice_client,
                url=f"/v1/me/chats/{chat_id}/messages",
                params=params,
            ),
            iter_paginated_endpoint(
                client=bob_client,
                url=f"/v1/me/chats/{chat_id}/messages",
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
