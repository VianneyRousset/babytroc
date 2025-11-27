from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.app import create_app
from app.config import Config
from app.schemas.user.private import UserPrivateRead

from .users import UserData


@pytest.fixture
async def client(
    app_config: Config,
) -> AsyncGenerator[AsyncClient]:
    """HTTP client to the app."""
    async with await create_client(app_config) as client:
        yield client


@pytest.fixture
async def alice_client(
    client: AsyncClient,
    alice: UserPrivateRead,
    alice_user_data: UserData,
) -> AsyncClient:
    """HTTP client to the app with Alice's credentials."""

    return await login_as_user(
        client=client,
        username=alice_user_data["email"],
        password=alice_user_data["password"],
    )


@pytest.fixture
async def bob_client(
    client: AsyncClient,
    bob: UserPrivateRead,
    bob_user_data: UserData,
) -> AsyncClient:
    """HTTP client to the app with Bob's credentials."""

    return await login_as_user(
        client=client,
        username=bob_user_data["email"],
        password=bob_user_data["password"],
    )


@pytest.fixture
async def carol_client(
    client: AsyncClient,
    carol: UserPrivateRead,
    carol_user_data: UserData,
) -> AsyncClient:
    """HTTP client to the app with Carol's credentials."""

    return await login_as_user(
        client=client,
        username=carol_user_data["email"],
        password=carol_user_data["password"],
    )


async def create_client(
    app_config: Config,
) -> AsyncClient:
    """Return a new http test client to the app."""

    app = await create_app(app_config)

    return AsyncClient(
        transport=ASGITransport(
            app=app,
            root_path="/api",
        ),
        base_url="https://babytroc.ch",
    )


async def login_as_user(
    client: AsyncClient,
    username: str,
    password: str,
) -> AsyncClient:
    """Login with `client` using `username` and `password`."""

    resp = await client.post(
        "https://babytroc.ch/api/v1/auth/login",
        data={
            "grant_type": "password",
            "username": username,
            "password": password,
        },
    )
    resp.raise_for_status()

    return client
