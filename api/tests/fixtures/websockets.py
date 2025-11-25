import asyncio
from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager
from types import TracebackType

import pytest
from httpx import AsyncClient
from httpx_ws import AsyncWebSocketSession, WebSocketDisconnect, aconnect_ws

from app.schemas.user.private import UserPrivateRead
from app.schemas.websocket import WebSocketMessage, WebSocketMessageTypeAdapter

from .users import UserData


@pytest.fixture
async def alice_websocket(
    alice_client: AsyncClient,
    alice: UserPrivateRead,
    alice_user_data: UserData,
) -> AsyncGenerator[AsyncWebSocketSession]:
    """Websocket with Alice's credentials."""

    ws: AsyncWebSocketSession
    async with aconnect_ws("/v1/me/websocket", alice_client) as ws:
        yield ws


@pytest.fixture
async def bob_websocket(
    bob_client: AsyncClient,
    bob: UserPrivateRead,
    bob_user_data: UserData,
) -> AsyncGenerator[AsyncWebSocketSession]:
    """Websocket with Bob's credentials."""

    ws: AsyncWebSocketSession
    async with aconnect_ws("/v1/me/websocket", bob_client) as ws:
        yield ws


@pytest.fixture
async def carol_websocket(
    carol_client: AsyncClient,
    carol: UserPrivateRead,
    carol_user_data: UserData,
) -> AsyncGenerator[AsyncWebSocketSession]:
    """Websocket with Carol's credentials."""

    ws: AsyncWebSocketSession
    async with aconnect_ws("/v1/me/websocket", carol_client) as ws:
        yield ws


class WebSocketRecorder(AbstractAsyncContextManager):
    """Helper to record one message from websocket."""

    WEBSOCKET_PATH = "/v1/me/websocket"

    def __init__(
        self,
        websocket: AsyncWebSocketSession,
        *,
        timeout: float | None = 2.0,
    ):
        self.websocket = websocket
        self.timeout = timeout
        self.message: WebSocketMessage | None = None

    async def __aenter__(self):
        await self.websocket.__aenter__()

        # trying to avoid some concurrency issues
        await asyncio.sleep(0.2)

        return self

    async def __aexit__(
        self,
        type: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        # record  message and close websocket
        if type is None:
            content = await self.websocket.receive_text()
            self.message = WebSocketMessageTypeAdapter.validate_json(content)

        await self.websocket.close()

        # wait for websocket close message
        try:
            await self.websocket.receive_text(timeout=self.timeout)
        except WebSocketDisconnect:
            pass

        await self.websocket.__aexit__(type, value, traceback)

        return None
