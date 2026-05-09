import pytest
from fastapi import status
from httpx import AsyncClient

from babytroc.domains.chat.schemas.read import ChatMessageRead, ChatRead
from babytroc.domains.item.schemas.read import ItemRead
from babytroc.domains.loan.schemas.read import LoanRequestRead
from babytroc.domains.user.schemas.private import UserPrivateRead

pytestmark = pytest.mark.timeout(30)


class TestForbiddenChatOperations:
    """Tests forbidden chat operations."""

    async def test_send_message_non_existing_chat(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        alice_new_item: ItemRead,
    ):
        """Check user cannot send a text message to an non-existing chat."""

        chat_id = f"{alice_new_item.id}-{bob.id}"

        # ensure chat does not exist
        res = await alice_client.get(f"/api/v1/me/chats/{chat_id}")
        assert res.status_code == status.HTTP_404_NOT_FOUND, "chat should not exist"

        # ensure cannot send message
        res = await alice_client.post(
            f"/api/v1/me/chats/{chat_id}/messages",
            json={"text": "test"},
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND, (
            "Alice should not be able to post in non-existing chat"
        )
        res = await bob_client.post(
            f"/api/v1/me/chats/{chat_id}/messages",
            json={"text": "test"},
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND, (
            "Bob should not be able to post in non-existing chat"
        )

    async def test_send_message_not_member(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        carol: UserPrivateRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        carol_client: AsyncClient,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that Carol cannot send a message in chat between Alice and Bob."""

        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        # check that Carol is not member of the chat
        res = await alice_client.get(f"/api/v1/me/chats/{chat_id}")
        res.raise_for_status()
        chat = ChatRead.model_validate(res.json())
        assert chat.borrower.id != carol.id, "Carol should not be part of the chat"
        assert chat.owner.id != carol.id, "Carol should not be part of the chat"

        # Carol should not be able to send a message in this chat
        res = await carol_client.post(
            f"/api/v1/me/chats/{chat_id}/messages",
            json={"text": "test"},
        )
        assert res.is_error

        # verify no message from Carol ended up in the chat
        res = await alice_client.get(
            f"/api/v1/me/chats/{chat_id}/messages"
        )
        assert all(msg["sender_id"] != carol.id for msg in res.json())

        res = await bob_client.get(
            f"/api/v1/me/chats/{chat_id}/messages"
        )
        assert all(msg["sender_id"] != carol.id for msg in res.json())

    async def test_cannot_read_chat_not_member(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        carol: UserPrivateRead,
        alice_client: AsyncClient,
        carol_client: AsyncClient,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
        carol_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check Carol cannot read the chat between Alice and Bob."""

        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        # check that Carol is not member of the chat
        res = await alice_client.get(f"/api/v1/me/chats/{chat_id}")
        res.raise_for_status()
        chat = ChatRead.model_validate(res.json())
        assert chat.borrower.id != carol.id, "Carol should not be part of the chat"
        assert chat.owner.id != carol.id, "Carol should not be part of the chat"

        # check chat contain at least one message
        res = await alice_client.get(f"/api/v1/me/chats/{chat_id}")
        assert res.is_success, "chat should exist"
        res = await alice_client.get(
            f"/api/v1/me/chats/{chat_id}/messages"
        )
        messages = res.json()
        assert len(messages) > 0, "the chat should a least contain one message"
        message = ChatMessageRead.model_validate(messages[0])

        # check cannot read chat
        res = await carol_client.get(f"/api/v1/me/chats/{chat_id}")
        assert res.is_error, "Carol should not be able to read chat"

        # check cannot read chat message
        res = await carol_client.get(
            f"/api/v1/me/chats/{chat_id}/messages"
        )
        assert res.is_error, "Carol should not be able to read chat messages"
        res = await carol_client.get(
            f"/api/v1/me/chats/{chat_id}/messages/{message.id}"
        )
        assert res.is_error, "Carol should not be able to read chat message"

        carol_chat_id = carol_new_loan_request_for_alice_new_item.chat_id
        res = await carol_client.get(
            f"/api/v1/me/chats/{carol_chat_id}/messages/{message.id}"
        )
        assert res.is_error, "Carol should not be able to read chat message"

    async def test_text_message_sent_to_proper_chat(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        carol: UserPrivateRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        carol_client: AsyncClient,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
        bob_new_loan_request_for_alice_special_item: LoanRequestRead,
        carol_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Ensure text messages sent between in a given chat, is not sent to others."""

        main_chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        other_chat_id_1 = bob_new_loan_request_for_alice_special_item.chat_id
        other_chat_id_2 = carol_new_loan_request_for_alice_new_item.chat_id

        res = await alice_client.post(
            f"/api/v1/me/chats/{main_chat_id}/messages",
            json={"text": "test"},
        )
        res.raise_for_status()
        message = ChatMessageRead.model_validate(res.json())

        # check message properly received
        res = await alice_client.get(
            f"/api/v1/me/chats/{main_chat_id}/messages"
        )
        assert res.json()[0]["id"] == message.id, (
            "Last message receive by Alice is not the sent message"
        )
        res = await bob_client.get(
            f"/api/v1/me/chats/{main_chat_id}/messages"
        )
        assert res.json()[0]["id"] == message.id, (
            "Last message receive by Bob is not the sent message"
        )

        # check the message is not in the other chat number 1
        res = await alice_client.get(
            f"/api/v1/me/chats/{other_chat_id_1}/messages"
        )
        assert all(msg["id"] != message.id for msg in res.json()), (
            "message should not be in this chat"
        )

        res = await bob_client.get(
            f"/api/v1/me/chats/{other_chat_id_1}/messages"
        )
        assert all(msg["id"] != message.id for msg in res.json()), (
            "message should not be in this chat"
        )
        res = await alice_client.get(
            f"/api/v1/me/chats/{other_chat_id_1}/messages/{message.id}"
        )
        assert res.is_error, "message should not be accessible from other chat"
        res = await bob_client.get(
            f"/api/v1/me/chats/{other_chat_id_1}/messages/{message.id}"
        )
        assert res.is_error, "message should not be accessible from other chat"

        # check the message is not in the other chat number 2
        res = await alice_client.get(
            f"/api/v1/me/chats/{other_chat_id_2}/messages"
        )
        assert all(msg["id"] != message.id for msg in res.json()), (
            "message should not be in this chat"
        )

        res = await carol_client.get(
            f"/api/v1/me/chats/{other_chat_id_2}/messages"
        )
        assert all(msg["id"] != message.id for msg in res.json()), (
            "message should not be in this chat"
        )

        res = await alice_client.get(
            f"/api/v1/me/chats/{other_chat_id_2}/messages/{message.id}"
        )
        assert res.is_error, "message should not be accessible from other chat"

        res = await carol_client.get(
            f"/api/v1/me/chats/{other_chat_id_2}/messages/{message.id}"
        )
        assert res.is_error, "message should not be accessible from other chat"
