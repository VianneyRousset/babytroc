import jwt
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from httpx_ws import AsyncWebSocketSession, aconnect_ws

pytestmark = pytest.mark.timeout(30)

from app.schemas.loan.read import LoanRequestRead
from app.schemas.user.private import UserPrivateRead
from app.schemas.websocket import (
    WebSocketMessageNewChatMessage,
    WebSocketMessageUpdatedChatMessage,
)
from tests.fixtures.clients import create_client
from tests.fixtures.websockets import WebSocketRecorder


class TestWebSocketAuth:
    """Test WebSocket authentication."""

    async def test_websocket_no_auth(
        self,
        app: FastAPI,
    ):
        """Connection without credentials should be rejected."""
        client = create_client(app)
        async with client:
            with pytest.raises(Exception):
                async with aconnect_ws("/api/v1/me/websocket", client):
                    pass

    async def test_websocket_expired_token(
        self,
        app: FastAPI,
        app_config,
    ):
        """Connection with expired JWT should be rejected."""
        from datetime import UTC, datetime, timedelta

        expired_token = jwt.encode(
            {
                "iat": datetime.now(UTC) - timedelta(hours=2),
                "exp": datetime.now(UTC) - timedelta(hours=1),
                "sub": "1",
                "validated": True,
            },
            key=app_config.auth.secret_key,
            algorithm=app_config.auth.algorithm,
        )
        client = create_client(app)
        async with client:
            client.cookies.set("Authorization", f"Bearer {expired_token}")
            with pytest.raises(Exception):
                async with aconnect_ws("/api/v1/me/websocket", client):
                    pass

    async def test_websocket_malformed_token(
        self,
        app: FastAPI,
    ):
        """Connection with bad token should be rejected."""
        client = create_client(app)
        async with client:
            client.cookies.set("Authorization", "Bearer garbage.token.here")
            with pytest.raises(Exception):
                async with aconnect_ws("/api/v1/me/websocket", client):
                    pass


class TestWebSocketRelay:
    """Test WebSocket message relay."""

    async def test_websocket_new_message_relay(
        self,
        alice_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_client: AsyncClient,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """New chat message is relayed via WebSocket."""
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        # drain pending messages from fixture setup
        try:
            while True:
                await alice_websocket.receive_text(timeout=0.5)
        except TimeoutError:
            pass

        recorder = WebSocketRecorder(alice_websocket)
        async with recorder:
            resp = await bob_client.post(
                f"/api/v1/me/chats/{chat_id}/messages",
                json={"text": "hello from bob"},
            )
            resp.raise_for_status()

        assert any(
            isinstance(msg, WebSocketMessageNewChatMessage)
            for msg in recorder.messages
        ), (
            f"Expected WebSocketMessageNewChatMessage, got: "
            f"{[type(m).__name__ for m in recorder.messages]}"
        )

    async def test_websocket_seen_update_relay(
        self,
        alice: UserPrivateRead,
        alice_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_client: AsyncClient,
        bob_websocket: AsyncWebSocketSession,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Marking a message as seen is relayed via WebSocket."""
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        # send a message
        resp = await alice_client.post(
            f"/api/v1/me/chats/{chat_id}/messages",
            json={"text": "test seen"},
        )
        resp.raise_for_status()
        message_id = resp.json()["id"]

        # drain pending messages
        for ws in [alice_websocket, bob_websocket]:
            try:
                while True:
                    await ws.receive_text(timeout=0.5)
            except TimeoutError:
                pass

        recorder_alice = WebSocketRecorder(alice_websocket)
        recorder_bob = WebSocketRecorder(bob_websocket)

        async with recorder_alice, recorder_bob:
            resp = await bob_client.post(
                f"/api/v1/me/chats/{chat_id}/messages/{message_id}/see"
            )
            resp.raise_for_status()

        for recorder in [recorder_alice, recorder_bob]:
            assert any(
                isinstance(msg, WebSocketMessageUpdatedChatMessage)
                for msg in recorder.messages
            ), (
                f"Expected WebSocketMessageUpdatedChatMessage, got: "
                f"{[type(m).__name__ for m in recorder.messages]}"
            )


@pytest.mark.usefixtures("items")
class TestWebSocketIsolation:
    """Test WebSocket channel isolation."""

    async def test_websocket_isolation(
        self,
        alice_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_websocket: AsyncWebSocketSession,
        carol_client: AsyncClient,
        carol_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Only chat members receive WebSocket notifications."""
        chat_id = carol_new_loan_request_for_alice_new_item.chat_id

        # drain pending messages
        for ws in [alice_websocket, bob_websocket]:
            try:
                while True:
                    await ws.receive_text(timeout=0.5)
            except TimeoutError:
                pass

        recorder_alice = WebSocketRecorder(alice_websocket)
        recorder_bob = WebSocketRecorder(bob_websocket)

        async with recorder_alice, recorder_bob:
            resp = await carol_client.post(
                f"/api/v1/me/chats/{chat_id}/messages",
                json={"text": "carol to alice"},
            )
            resp.raise_for_status()

        # Alice should have received the message (she's in the chat)
        assert any(
            isinstance(msg, WebSocketMessageNewChatMessage)
            for msg in recorder_alice.messages
        ), "Alice should receive the message"

        # Bob should NOT have received anything
        assert not any(
            isinstance(msg, WebSocketMessageNewChatMessage)
            for msg in recorder_bob.messages
        ), (
            f"Bob should not receive messages, got: "
            f"{[type(m).__name__ for m in recorder_bob.messages]}"
        )
