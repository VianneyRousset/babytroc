from fastapi import status
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession
import pytest

from time import sleep
from starlette.websockets import WebSocketDisconnect
from app.enums import ChatMessageType
from app.schemas.chat.read import ChatMessageRead, ChatRead
from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRead, LoanRequestRead
from app.schemas.user.private import UserPrivateRead
from app.schemas.websocket import (
    WebSocketMessageNewChatMessage,
    WebSocketMessageUpdatedChatMessage,
)
from tests.fixtures.websockets import WebSocketRecorder


class TestChatMessage:
    """Tests on chat messages."""

    def test_message_text(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that text messages are transmitted."""

        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        text = "hello"

        alice_websocket_recorder = WebSocketRecorder(alice_websocket)
        bob_websocket_recorder = WebSocketRecorder(bob_websocket)
        with alice_websocket_recorder, bob_websocket_recorder:
            # send text message
            resp = alice_client.post(
                f"/v1/me/chats/{chat_id}/messages",
                json={"text": text},
            )
            resp.raise_for_status()

        assert isinstance(
            alice_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            bob_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = alice_websocket_recorder.message.message

        # construct expected chat message
        expected_chat_message = ChatMessageRead(
            id=alice_chat_message.id,
            chat_id=chat_id,
            message_type=ChatMessageType.text,
            sender_id=alice.id,
            creation_date=alice_chat_message.creation_date,
            seen=False,
            text=text,
            loan_request_id=None,
            loan_id=None,
            item_id=alice_new_item.id,
            borrower_id=bob.id,
        )

        # construct expected websocket message
        expected_websocket_message = WebSocketMessageNewChatMessage(
            type="new_chat_message",
            message=expected_chat_message,
        )

        # check websocket messages
        assert (
            alice_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            bob_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )

        # check a chat message has been created for alice
        resp = alice_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

        # check a chat message has been created for bob
        resp = bob_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

    def test_message_loan_request_created(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
    ):
        """Check that creating a loan request sends a chat message."""

        alice_websocket_recorder = WebSocketRecorder(alice_websocket)
        bob_websocket_recorder = WebSocketRecorder(bob_websocket)
        with alice_websocket_recorder, bob_websocket_recorder:
            # request item
            resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
            resp.raise_for_status()
            loan_request = LoanRequestRead.model_validate_json(resp.text)

        assert isinstance(
            alice_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            bob_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = alice_websocket_recorder.message.message

        # construct expected chat message
        expected_chat_message = ChatMessageRead(
            id=alice_chat_message.id,
            chat_id=loan_request.chat_id,
            message_type=ChatMessageType.loan_request_created,
            sender_id=bob.id,
            creation_date=alice_chat_message.creation_date,
            seen=False,
            text=None,
            loan_request_id=loan_request.id,
            loan_id=None,
            item_id=alice_new_item.id,
            borrower_id=bob.id,
        )

        # construct expected websocket message
        expected_websocket_message = WebSocketMessageNewChatMessage(
            type="new_chat_message",
            message=expected_chat_message,
        )

        # check websocket messages
        assert (
            alice_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            bob_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )

        # check a chat message has been created for alice
        resp = alice_client.get(f"/v1/me/chats/{loan_request.chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

        # check a chat message has been created for bob
        resp = bob_client.get(f"/v1/me/chats/{loan_request.chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

    def test_loan_request_cancelled_message(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that cancelling a loan request sends a chat message."""

        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        alice_websocket_recorder = WebSocketRecorder(alice_websocket)
        bob_websocket_recorder = WebSocketRecorder(bob_websocket)
        with alice_websocket_recorder, bob_websocket_recorder:
            # cancel loan request
            bob_client.delete(
                f"/v1/items/{alice_new_item.id}/request"
            ).raise_for_status()

        assert isinstance(
            alice_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            bob_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = alice_websocket_recorder.message.message

        # construct expected chat message
        expected_chat_message = ChatMessageRead(
            id=alice_chat_message.id,
            chat_id=bob_new_loan_request_for_alice_new_item.chat_id,
            message_type=ChatMessageType.loan_request_cancelled,
            sender_id=bob.id,
            creation_date=alice_chat_message.creation_date,
            seen=False,
            text=None,
            loan_request_id=bob_new_loan_request_for_alice_new_item.id,
            loan_id=None,
            item_id=alice_new_item.id,
            borrower_id=bob.id,
        )

        # construct expected websocket message
        expected_websocket_message = WebSocketMessageNewChatMessage(
            type="new_chat_message",
            message=expected_chat_message,
        )

        # check websocket messages
        assert (
            alice_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            bob_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )

        # check a chat message has been created for alice
        resp = alice_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

        # check a chat message has been created for bob
        resp = bob_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

    def test_loan_request_rejected_message(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that rejecting a loan request sends a chat message."""

        loan_request_id = bob_new_loan_request_for_alice_new_item.id
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        alice_websocket_recorder = WebSocketRecorder(alice_websocket)
        bob_websocket_recorder = WebSocketRecorder(bob_websocket)
        with alice_websocket_recorder, bob_websocket_recorder:
            # reject loan request
            alice_client.post(
                f"/v1/me/items/{alice_new_item.id}/requests/{loan_request_id}/reject"
            ).raise_for_status()

        assert isinstance(
            alice_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            bob_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = alice_websocket_recorder.message.message

        # construct expected chat message
        expected_chat_message = ChatMessageRead(
            id=alice_chat_message.id,
            chat_id=bob_new_loan_request_for_alice_new_item.chat_id,
            message_type=ChatMessageType.loan_request_rejected,
            sender_id=alice.id,
            creation_date=alice_chat_message.creation_date,
            seen=False,
            text=None,
            loan_request_id=bob_new_loan_request_for_alice_new_item.id,
            loan_id=None,
            item_id=alice_new_item.id,
            borrower_id=bob.id,
        )

        # construct expected websocket message
        expected_websocket_message = WebSocketMessageNewChatMessage(
            type="new_chat_message",
            message=expected_chat_message,
        )

        # check websocket messages
        assert (
            alice_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            bob_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )

        # check a chat message has been created for alice
        resp = alice_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

        # check a chat message has been created for bob
        resp = bob_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

    def test_loan_request_accepted_message(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that accepting a loan request sends a chat message."""

        loan_request_id = bob_new_loan_request_for_alice_new_item.id
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        alice_websocket_recorder = WebSocketRecorder(alice_websocket)
        bob_websocket_recorder = WebSocketRecorder(bob_websocket)
        with alice_websocket_recorder, bob_websocket_recorder:
            # accept loan request
            alice_client.post(
                f"/v1/me/items/{alice_new_item.id}/requests/{loan_request_id}/accept"
            ).raise_for_status()

        assert isinstance(
            alice_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            bob_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = alice_websocket_recorder.message.message

        # construct expected chat message
        expected_chat_message = ChatMessageRead(
            id=alice_chat_message.id,
            chat_id=bob_new_loan_request_for_alice_new_item.chat_id,
            message_type=ChatMessageType.loan_request_accepted,
            sender_id=alice.id,
            creation_date=alice_chat_message.creation_date,
            seen=False,
            text=None,
            loan_request_id=bob_new_loan_request_for_alice_new_item.id,
            loan_id=None,
            item_id=alice_new_item.id,
            borrower_id=bob.id,
        )

        # construct expected websocket message
        expected_websocket_message = WebSocketMessageNewChatMessage(
            type="new_chat_message",
            message=expected_chat_message,
        )

        # check websocket messages
        assert (
            alice_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            bob_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )

        # check a chat message has been created for alice
        resp = alice_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

        # check a chat message has been created for bob
        resp = bob_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

    def test_loan_started_message(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that executing a loan request sends a chat message."""

        loan_request_id = bob_new_loan_request_for_alice_new_item.id
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        # accept loan request
        alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{loan_request_id}/accept"
        ).raise_for_status()

        alice_websocket_recorder = WebSocketRecorder(alice_websocket)
        bob_websocket_recorder = WebSocketRecorder(bob_websocket)
        with alice_websocket_recorder, bob_websocket_recorder:
            # execute loan request
            bob_client.post(
                f"/v1/me/borrowings/requests/{loan_request_id}/execute"
            ).raise_for_status()

        assert isinstance(
            alice_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            bob_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = alice_websocket_recorder.message.message

        # construct expected chat message
        expected_chat_message = ChatMessageRead(
            id=alice_chat_message.id,
            chat_id=bob_new_loan_request_for_alice_new_item.chat_id,
            message_type=ChatMessageType.loan_started,
            sender_id=bob.id,
            creation_date=alice_chat_message.creation_date,
            seen=False,
            text=None,
            loan_request_id=None,
            loan_id=alice_chat_message.loan_id,
            item_id=alice_new_item.id,
            borrower_id=bob.id,
        )

        # construct expected websocket message
        expected_websocket_message = WebSocketMessageNewChatMessage(
            type="new_chat_message",
            message=expected_chat_message,
        )

        # check websocket messages
        assert (
            alice_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            bob_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )

        # check a chat message has been created for alice
        resp = alice_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

        # check a chat message has been created for bob
        resp = bob_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

    def test_loan_ended_message(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
        bob_new_loan_of_alice_new_item: LoanRead,
    ):
        """Check that ending a loan sends a chat message."""

        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        loan_id = bob_new_loan_of_alice_new_item.id

        alice_websocket_recorder = WebSocketRecorder(alice_websocket)
        bob_websocket_recorder = WebSocketRecorder(bob_websocket)
        with alice_websocket_recorder, bob_websocket_recorder:
            # end loan
            alice_client.post(
                f"/v1/me/loans/{loan_id}/end",
            ).raise_for_status()

        assert isinstance(
            alice_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            bob_websocket_recorder.message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = alice_websocket_recorder.message.message

        # construct expected chat message
        expected_chat_message = ChatMessageRead(
            id=alice_chat_message.id,
            chat_id=chat_id,
            message_type=ChatMessageType.loan_ended,
            sender_id=alice.id,
            creation_date=alice_chat_message.creation_date,
            seen=False,
            text=None,
            loan_request_id=None,
            loan_id=loan_id,
            item_id=alice_new_item.id,
            borrower_id=bob.id,
        )

        # construct expected websocket message
        expected_websocket_message = WebSocketMessageNewChatMessage(
            type="new_chat_message",
            message=expected_chat_message,
        )

        # check websocket messages
        assert (
            alice_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            bob_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )

        # check a chat message has been created for alice
        resp = alice_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

        # check a chat message has been created for bob
        resp = bob_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

    def test_mark_message_as_seen(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that seeing a message mark it as read and emit a websocket message."""

        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        text = "hello"

        # send text message
        resp = alice_client.post(
            f"/v1/me/chats/{chat_id}/messages",
            json={"text": text},
        )
        resp.raise_for_status()
        message = ChatMessageRead.model_validate_json(resp.text)

        alice_websocket_recorder = WebSocketRecorder(alice_websocket)
        bob_websocket_recorder = WebSocketRecorder(bob_websocket)
        with alice_websocket_recorder, bob_websocket_recorder:
            resp = bob_client.post(f"/v1/me/chats/{chat_id}/messages/{message.id}/see")
            resp.raise_for_status()

        assert isinstance(
            alice_websocket_recorder.message, WebSocketMessageUpdatedChatMessage
        )

        assert isinstance(
            bob_websocket_recorder.message, WebSocketMessageUpdatedChatMessage
        )

        alice_chat_message = alice_websocket_recorder.message.message

        # construct expected chat message
        expected_chat_message = ChatMessageRead(
            id=alice_chat_message.id,
            chat_id=chat_id,
            message_type=ChatMessageType.text,
            sender_id=alice.id,
            creation_date=alice_chat_message.creation_date,
            seen=True,
            text=text,
            loan_request_id=None,
            loan_id=None,
            item_id=alice_new_item.id,
            borrower_id=bob.id,
        )

        # construct expected websocket message
        expected_websocket_message = WebSocketMessageUpdatedChatMessage(
            type="updated_chat_message",
            message=expected_chat_message,
        )

        # check websocket messages
        assert (
            alice_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            bob_websocket_recorder.message.model_dump()
            == expected_websocket_message.model_dump()
        )

        # check a chat message has been created for alice
        resp = alice_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()

        # check a chat message has been created for bob
        resp = bob_client.get(f"/v1/me/chats/{chat_id}/messages")
        resp.raise_for_status()
        last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
        assert last_chat_message.model_dump() == expected_chat_message.model_dump()


class TestChatForbiddenTextMessage:
    """Tests sending message to an non-existing chat."""

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
        assert alice_client.post(
            f"/v1/me/chats/{chat_id}/messages", json={"text": "test"}
        ).is_error, "Alice should not be able to post in non-exist chat"
        assert bob_client.post(
            f"/v1/me/chats/{chat_id}/messages", json={"text": "test"}
        ).is_error, "Bob should not be able to post in non-exist chat"

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
        """Check Carol cannot send a message in chat between Alice and Bob."""

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


class TestChatReadSeparation:
    """Tests proper separation of the chats."""

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
