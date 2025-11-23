from time import sleep

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession
from starlette.websockets import WebSocketDisconnect

from app.schemas.chat.read import ChatMessageRead, ChatRead
from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRequestRead
from app.schemas.user.private import UserPrivateRead


class TestForbiddenChatOperations:
    """Tests forbidden chat operations."""

    def test_send_message_non_existing_chat(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_new_item: ItemRead,
    ):
        """Check user cannot send a text message to an non-existing chat."""

        chat_id = f"{alice_new_item.id}-{bob.id}"

        # ensure chat does not exist
        assert (
            alice_client.get(f"/v1/me/chats/{chat_id}").status_code
            == status.HTTP_404_NOT_FOUND
        ), "chat should not exist"

        # ensure cannot send message
        assert (
            alice_client.post(
                f"/v1/me/chats/{chat_id}/messages", json={"text": "test"}
            ).status_code
            == status.HTTP_404_NOT_FOUND
        ), "Alice should not be able to post in non-existing chat"
        assert (
            bob_client.post(
                f"/v1/me/chats/{chat_id}/messages", json={"text": "test"}
            ).status_code
            == status.HTTP_404_NOT_FOUND
        ), "Bob should not be able to post in non-existing chat"

    def test_send_message_not_member(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        carol: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        carol_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that Carol cannot send a message in chat between Alice and Bob."""

        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        # check that Carol is not member of the chat
        chat = ChatRead.model_validate(
            alice_client.get(f"/v1/me/chats/{chat_id}").json()
        )
        assert chat.borrower.id != carol.id, "Carol should not be part of the chat"
        assert chat.owner.id != carol.id, "Carol should not be part of the chat"

        with alice_websocket, bob_websocket:
            sleep(0.2)

            # check message cannot be sent
            assert carol_client.post(
                f"/v1/me/chats/{chat_id}.messages", json={"text": "test"}
            ).is_error

            sleep(0.2)

            alice_websocket.close()
            bob_websocket.close()

            # ensure Alice didn't receive any message via websockett
            with pytest.raises(WebSocketDisconnect):
                alice_websocket.receive_text()

            # ensure Bob didn't receive any message via websockett
            with pytest.raises(WebSocketDisconnect):
                bob_websocket.receive_text()

        # ensure there is no message from Carol
        assert all(
            msg["sender_id"] != carol.id
            for msg in alice_client.get(f"/v1/me/chats/{chat_id}/messages").json()
        )
        assert all(
            msg["sender_id"] != carol.id
            for msg in bob_client.get(f"/v1/me/chats/{chat_id}/messages").json()
        )

    def test_cannot_read_chat_not_member(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        carol: UserPrivateRead,
        alice_client: TestClient,
        carol_client: TestClient,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
        carol_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check Carol cannot read the chat between Alice and Bob."""

        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        # check that Carol is not member of the chat
        chat = ChatRead.model_validate(
            alice_client.get(f"/v1/me/chats/{chat_id}").json()
        )
        assert chat.borrower.id != carol.id, "Carol should not be part of the chat"
        assert chat.owner.id != carol.id, "Carol should not be part of the chat"

        # check chat contain at least one message
        assert alice_client.get(f"/v1/me/chats/{chat_id}").is_success, (
            "chat should exist"
        )
        messages = alice_client.get(f"/v1/me/chats/{chat_id}/messages").json()
        assert len(messages) > 0, "the chat should a least contain one message"
        message = ChatMessageRead.model_validate(messages[0])

        # check cannot read chat
        assert carol_client.get(f"/v1/me/chats/{chat_id}").is_error, (
            "Carol should not be able to read chat"
        )

        # check cannot read chat message
        assert carol_client.get(f"/v1/me/chats/{chat_id}/messages").is_error, (
            "Carol should not be able to read chat messages"
        )
        assert carol_client.get(
            f"/v1/me/chats/{chat_id}/messages/{message.id}"
        ).is_error, "Carol should not be able to read chat message"

        carol_chat_id = carol_new_loan_request_for_alice_new_item.chat_id
        assert carol_client.get(
            f"/v1/me/chats/{carol_chat_id}/messages/{message.id}"
        ).is_error, "Carol should not be able to read chat message"

    def test_text_message_sent_to_proper_chat(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        carol: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        carol_client: TestClient,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
        bob_new_loan_request_for_alice_special_item: LoanRequestRead,
        carol_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Ensure text messages sent between in a given chat, is not sent to others."""

        main_chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        other_chat_id_1 = bob_new_loan_request_for_alice_special_item.chat_id
        other_chat_id_2 = carol_new_loan_request_for_alice_new_item.chat_id

        message = ChatMessageRead.model_validate(
            alice_client.post(
                f"/v1/me/chats/{main_chat_id}/messages", json={"text": "test"}
            ).json()
        )

        # check message properly received
        assert (
            alice_client.get(f"/v1/me/chats/{main_chat_id}/messages").json()[0]["id"]
            == message.id
        ), "Last message receive by Alice is not the sent message"
        assert (
            bob_client.get(f"/v1/me/chats/{main_chat_id}/messages").json()[0]["id"]
            == message.id
        ), "Last message receive by Bob is not the sent message"

        # check the message is not in the other chat number 1
        assert all(
            msg["id"] != message.id
            for msg in alice_client.get(
                f"/v1/me/chats/{other_chat_id_1}/messages"
            ).json()
        ), "message should not be in this chat"
        assert all(
            msg["id"] != message.id
            for msg in bob_client.get(f"/v1/me/chats/{other_chat_id_1}/messages").json()
        ), "message should not be in this chat"
        assert alice_client.get(f"/v1/me/chats/{other_chat_id_1}/messages/{message.id}")
        assert bob_client.get(f"/v1/me/chats/{other_chat_id_1}/messages/{message.id}")

        # check the message is not in the other chat number 2
        assert all(
            msg["id"] != message.id
            for msg in alice_client.get(
                f"/v1/me/chats/{other_chat_id_2}/messages"
            ).json()
        ), "message should not be in this chat"
        assert all(
            msg["id"] != message.id
            for msg in carol_client.get(
                f"/v1/me/chats/{other_chat_id_2}/messages"
            ).json()
        ), "message should not be in this chat"
        assert alice_client.get(f"/v1/me/chats/{other_chat_id_2}/messages/{message.id}")
        assert carol_client.get(f"/v1/me/chats/{other_chat_id_2}/messages/{message.id}")
