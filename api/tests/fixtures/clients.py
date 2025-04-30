import pytest
from fastapi.testclient import TestClient

from app.app import create_app
from app.config import Config
from app.schemas.user.private import UserPrivateRead

from .users import UserData


@pytest.fixture
def client(
    app_config: Config,
) -> TestClient:
    """HTTP client to the app."""
    return create_client(app_config)


@pytest.fixture
def alice_client(
    app_config: Config,
    alice: UserPrivateRead,
    alice_user_data: UserData,
) -> TestClient:
    """HTTP client to the app with Alice's credentials."""

    return login_as_user(
        client=create_client(app_config),
        username=alice_user_data["email"],
        password=alice_user_data["password"],
    )


@pytest.fixture
def bob_client(
    app_config: Config,
    bob: UserPrivateRead,
    bob_user_data: UserData,
) -> TestClient:
    """HTTP client to the app with Bob's credentials."""

    return login_as_user(
        client=create_client(app_config),
        username=bob_user_data["email"],
        password=bob_user_data["password"],
    )


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
