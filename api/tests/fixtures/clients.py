from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession

from app.app import create_app
from app.config import Config
from app.schemas.user.private import UserPrivateRead

from .users import UserData


@pytest.fixture
def client(
    app_config: Config,
) -> Generator[TestClient]:
    """HTTP client to the app."""
    with create_client(app_config) as client:
        yield client


@pytest.fixture
def alice_client(
    app_config: Config,
    alice: UserPrivateRead,
    alice_user_data: UserData,
) -> Generator[TestClient]:
    """HTTP client to the app with Alice's credentials."""

    with create_client(app_config) as client:
        yield login_as_user(
            client=client,
            username=alice_user_data["email"],
            password=alice_user_data["password"],
        )


@pytest.fixture
def bob_client(
    app_config: Config,
    bob: UserPrivateRead,
    bob_user_data: UserData,
) -> Generator[TestClient]:
    """HTTP client to the app with Bob's credentials."""

    with create_client(app_config) as client:
        yield login_as_user(
            client=client,
            username=bob_user_data["email"],
            password=bob_user_data["password"],
        )


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


# TODO share app ?
def create_client(
    app_config: Config,
) -> TestClient:
    """Return a new http test client to the app."""
    return TestClient(create_app(app_config))


def login_as_user(
    client: TestClient,
    username: str,
    password: str,
) -> TestClient:
    """Login with `client` using `username` and `password`."""

    client.post(
        "/v1/auth/login",
        data={
            "grant_type": "password",
            "username": username,
            "password": password,
        },
    ).raise_for_status()

    return client
