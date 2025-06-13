from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession

from app.enums import ChatMessageType
from app.schemas.chat.read import ChatMessageRead
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
