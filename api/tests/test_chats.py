from contextlib import AbstractContextManager
from time import sleep
from types import TracebackType
from typing import cast

from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession
from starlette.websockets import WebSocketDisconnect

from app.enums import ChatMessageType
from app.schemas.chat.read import ChatMessageRead
from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRead, LoanRequestRead
from app.schemas.user.private import UserPrivateRead
from app.schemas.websocket import WebSocketMessage, WebSocketMessageNewChatMessage


class WebSocketsRecorder(AbstractContextManager):
    """Helper to record one message from websockets."""

    WEBSOCKET_PATH = "/v1/me/websocket"

    def __init__(
        self,
        *,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
    ):
        self.alice_websocket = alice_websocket
        self.bob_websocket = bob_websocket

        self.alice_websocket_message = cast("WebSocketMessage | None", None)
        self.bob_websocket_message = cast("WebSocketMessage | None", None)

    def __enter__(self):
        self.alice_websocket.__enter__()
        self.bob_websocket.__enter__()

        # trying to avoid some concurrency issues
        sleep(0.2)

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        # record alice message and close websocket
        content = self.alice_websocket.receive_text()
        self.alice_websocket_message = WebSocketMessage.model_validate_json(content)
        self.alice_websocket.close()

        # record alice message and close websocket
        content = self.bob_websocket.receive_text()
        self.bob_websocket_message = WebSocketMessage.model_validate_json(content)
        self.bob_websocket.close()

        # wait for websocket close message
        try:
            self.alice_websocket.receive_text()
        except WebSocketDisconnect:
            pass

        try:
            self.bob_websocket.receive_text()
        except WebSocketDisconnect:
            pass

        self.alice_websocket.__exit__(None, None, None)
        self.bob_websocket.__exit__(None, None, None)

        return None


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

        recorder = WebSocketsRecorder(
            alice_websocket=alice_websocket,
            bob_websocket=bob_websocket,
        )
        with recorder:
            # send text message
            resp = alice_client.post(
                f"/v1/me/chats/{chat_id}/messages",
                json={"text": text},
            )
            resp.raise_for_status()

        assert isinstance(
            recorder.alice_websocket_message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            recorder.bob_websocket_message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = recorder.alice_websocket_message.message

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
            recorder.alice_websocket_message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            recorder.bob_websocket_message.model_dump()
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

        recorder = WebSocketsRecorder(
            alice_websocket=alice_websocket,
            bob_websocket=bob_websocket,
        )
        with recorder:
            # request item
            resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
            resp.raise_for_status()
            loan_request = LoanRequestRead.model_validate_json(resp.text)

        assert isinstance(
            recorder.alice_websocket_message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            recorder.bob_websocket_message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = recorder.alice_websocket_message.message

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
            recorder.alice_websocket_message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            recorder.bob_websocket_message.model_dump()
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

        recorder = WebSocketsRecorder(
            alice_websocket=alice_websocket,
            bob_websocket=bob_websocket,
        )
        with recorder:
            # cancel loan request
            bob_client.delete(
                f"/v1/items/{alice_new_item.id}/request"
            ).raise_for_status()

        assert isinstance(
            recorder.alice_websocket_message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            recorder.bob_websocket_message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = recorder.alice_websocket_message.message

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
            recorder.alice_websocket_message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            recorder.bob_websocket_message.model_dump()
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

        recorder = WebSocketsRecorder(
            alice_websocket=alice_websocket,
            bob_websocket=bob_websocket,
        )

        with recorder:
            # reject loan request
            alice_client.post(
                f"/v1/me/items/{alice_new_item.id}/requests/{loan_request_id}/reject"
            ).raise_for_status()

        assert isinstance(
            recorder.alice_websocket_message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            recorder.bob_websocket_message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = recorder.alice_websocket_message.message

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
            recorder.alice_websocket_message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            recorder.bob_websocket_message.model_dump()
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

        recorder = WebSocketsRecorder(
            alice_websocket=alice_websocket,
            bob_websocket=bob_websocket,
        )
        with recorder:
            # accept loan request
            alice_client.post(
                f"/v1/me/items/{alice_new_item.id}/requests/{loan_request_id}/accept"
            ).raise_for_status()

        assert isinstance(
            recorder.alice_websocket_message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            recorder.bob_websocket_message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = recorder.alice_websocket_message.message

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
            recorder.alice_websocket_message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            recorder.bob_websocket_message.model_dump()
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

        recorder = WebSocketsRecorder(
            alice_websocket=alice_websocket,
            bob_websocket=bob_websocket,
        )

        # accept loan request
        alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{loan_request_id}/accept"
        ).raise_for_status()

        with recorder:
            # execute loan request
            bob_client.post(
                f"/v1/me/borrowings/requests/{loan_request_id}/execute"
            ).raise_for_status()

        assert isinstance(
            recorder.alice_websocket_message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            recorder.bob_websocket_message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = recorder.alice_websocket_message.message

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
            recorder.alice_websocket_message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            recorder.bob_websocket_message.model_dump()
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

        recorder = WebSocketsRecorder(
            alice_websocket=alice_websocket,
            bob_websocket=bob_websocket,
        )

        with recorder:
            # end loan
            alice_client.post(
                f"/v1/me/loans/{loan_id}/end",
            ).raise_for_status()

        assert isinstance(
            recorder.alice_websocket_message, WebSocketMessageNewChatMessage
        )

        assert isinstance(
            recorder.bob_websocket_message, WebSocketMessageNewChatMessage
        )

        alice_chat_message = recorder.alice_websocket_message.message

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
            recorder.alice_websocket_message.model_dump()
            == expected_websocket_message.model_dump()
        )
        assert (
            recorder.bob_websocket_message.model_dump()
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
