import logging
from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from types import TracebackType

import pytest
from fastapi import FastAPI
from httpx_ws import AsyncWebSocketSession, WebSocketDisconnect, aconnect_ws

from app.domains.chat.schemas.websocket import WebSocketMessage, WebSocketMessageTypeAdapter

from .clients import create_client, login_as_user
from .users import UserData


@asynccontextmanager
async def _open_test_websocket(
    app: FastAPI,
    user_data: UserData,
) -> AsyncGenerator[AsyncWebSocketSession]:
    """Open a websocket connection for testing.

    Wraps aconnect_ws and suppresses cancel scope errors on teardown
    caused by pytest-asyncio running fixture cleanup in a different task.
    """
    client = create_client(app)
    await client.__aenter__()
    await login_as_user(
        client=client,
        username=user_data["email"],
        password=user_data["password"],
    )

    try:
        async with aconnect_ws(
            "/api/v1/me/websocket",
            client,
        ) as websocket:  # type: AsyncWebSocketSession
            yield websocket
    except RuntimeError as exc:
        if "cancel scope" not in str(exc):
            raise


@pytest.fixture
async def alice_websocket(
    app: FastAPI,
    alice_user_data: UserData,
) -> AsyncGenerator[AsyncWebSocketSession]:
    """Websocket with Alice's credentials."""

    async with _open_test_websocket(app, alice_user_data) as websocket:
        yield websocket


@pytest.fixture
async def bob_websocket(
    app: FastAPI,
    bob_user_data: UserData,
) -> AsyncGenerator[AsyncWebSocketSession]:
    """Websocket with Bob's credentials."""

    async with _open_test_websocket(app, bob_user_data) as websocket:
        yield websocket


@pytest.fixture
async def carol_websocket(
    app: FastAPI,
    carol_user_data: UserData,
) -> AsyncGenerator[AsyncWebSocketSession]:
    """Websocket with Carol's credentials."""

    async with _open_test_websocket(app, carol_user_data) as websocket:
        yield websocket


class WebSocketRecorder(AbstractAsyncContextManager):
    """Helper to record one message from websocket.

    On exit, receives all available messages (with timeout) and stores them.
    The checker can then find the matching message by type.
    """

    def __init__(
        self,
        websocket: AsyncWebSocketSession,
        *,
        timeout: float | None = 5.0,
    ):
        self.websocket = websocket
        self.timeout = timeout
        self.message: WebSocketMessage | None = None
        self.messages: list[WebSocketMessage] = []

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        _type: type[BaseException] | None,
        _value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> bool | None:
        # receive all available messages
        if _type is None:
            while True:
                try:
                    content = await self.websocket.receive_text(
                        timeout=self.timeout,
                    )
                except (TimeoutError, WebSocketDisconnect):
                    break
                msg = WebSocketMessageTypeAdapter.validate_json(content)
                self.messages.append(msg)

            # default: last message (backwards compatible)
            if self.messages:
                self.message = self.messages[-1]

        # close websocket
        try:
            await self.websocket.close()
        except Exception:
            logging.debug(
                "Failed to close websocket during recorder teardown",
                exc_info=True,
            )

        return None
