from collections.abc import Generator
from contextlib import AbstractContextManager
from time import sleep
from types import TracebackType

import pytest
from starlette.testclient import WebSocketTestSession
from starlette.websockets import WebSocketDisconnect

from app.config import Config
from app.schemas.user.private import UserPrivateRead
from app.schemas.websocket import (
    WebSocketMessage,
    WebSocketMessageTypeAdapter,
)

from .clients import create_client, login_as_user
from .users import UserData


@pytest.fixture
def alice_websocket(
    app_config: Config,
    alice: UserPrivateRead,
    alice_user_data: UserData,
) -> Generator[WebSocketTestSession]:
    """Websocket with Alice's credentials."""

    with create_client(app_config) as client:
        alice_client = login_as_user(
            client=client,
            username=alice_user_data["email"],
            password=alice_user_data["password"],
        )
        yield alice_client.websocket_connect("/v1/me/websocket")


@pytest.fixture
def bob_websocket(
    app_config: Config,
    bob: UserPrivateRead,
    bob_user_data: UserData,
) -> Generator[WebSocketTestSession]:
    """Websocket with Bob's credentials."""

    with create_client(app_config) as client:
        bob_client = login_as_user(
            client=client,
            username=bob_user_data["email"],
            password=bob_user_data["password"],
        )

        yield bob_client.websocket_connect("/v1/me/websocket")


class WebSocketRecorder(AbstractContextManager):
    """Helper to record one message from websocket."""

    WEBSOCKET_PATH = "/v1/me/websocket"

    def __init__(self, websocket: WebSocketTestSession):
        self.websocket = websocket
        self.message: WebSocketMessage | None = None

    def __enter__(self):
        self.websocket.__enter__()

        # trying to avoid some concurrency issues
        sleep(0.2)

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        # record  message and close websocket
        content = self.websocket.receive_text()
        self.message = WebSocketMessageTypeAdapter.validate_json(content)
        self.websocket.close()

        # wait for websocket close message
        try:
            self.websocket.receive_text()
        except WebSocketDisconnect:
            pass

        self.websocket.__exit__(None, None, None)

        return None
