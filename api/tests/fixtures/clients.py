import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from app.app import create_app
from app.config import Config, DatabaseConfig
from app.schemas.user.read import UserRead

from .users import UserData


@pytest.fixture
def client(
    database: sqlalchemy.URL,
) -> TestClient:
    """HTTP client to the app."""
    return create_client(database)


@pytest.fixture
def alice_client(
    database: sqlalchemy.URL,
    alice: UserRead,
    alice_user_data: UserData,
) -> TestClient:
    """HTTP client to the app with Alice's credentials."""

    return login_as_user(
        client=create_client(database),
        username=alice_user_data["email"],
        password=alice_user_data["password"],
    )


@pytest.fixture
def bob_client(
    database: sqlalchemy.URL,
    bob: UserRead,
    bob_user_data: UserData,
) -> TestClient:
    """HTTP client to the app with Bob's credentials."""

    return login_as_user(
        client=create_client(database),
        username=bob_user_data["email"],
        password=bob_user_data["password"],
    )


def create_client(
    database: sqlalchemy.URL,
) -> TestClient:
    """Return a new http test client to the app."""

    config = Config.from_env(database=DatabaseConfig.from_env(url=database))
    client = TestClient(create_app(config))
    return client


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
