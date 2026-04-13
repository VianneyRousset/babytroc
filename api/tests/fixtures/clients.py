from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from httpx_ws.transport import ASGIWebSocketTransport

from app.schemas.user.private import UserPrivateRead

from .users import UserData


@pytest.fixture
async def client(
    app: FastAPI,
) -> AsyncGenerator[AsyncClient]:
    """HTTP client to the app."""
    c = create_client(app)
    yield c
    await c.aclose()


@pytest.fixture
async def alice_client(
    app: FastAPI,
    alice: UserPrivateRead,
    alice_user_data: UserData,
) -> AsyncGenerator[AsyncClient]:
    """HTTP client to the app with Alice's credentials."""

    c = await login_as_user(
        client=create_client(app),
        username=alice_user_data["email"],
        password=alice_user_data["password"],
    )
    yield c
    await c.aclose()


@pytest.fixture
async def bob_client(
    app: FastAPI,
    bob: UserPrivateRead,
    bob_user_data: UserData,
) -> AsyncGenerator[AsyncClient]:
    """HTTP client to the app with Bob's credentials."""

    c = await login_as_user(
        client=create_client(app),
        username=bob_user_data["email"],
        password=bob_user_data["password"],
    )
    yield c
    await c.aclose()


@pytest.fixture
async def carol_client(
    app: FastAPI,
    carol: UserPrivateRead,
    carol_user_data: UserData,
) -> AsyncGenerator[AsyncClient]:
    """HTTP client to the app with Carol's credentials."""

    c = await login_as_user(
        client=create_client(app),
        username=carol_user_data["email"],
        password=carol_user_data["password"],
    )
    yield c
    await c.aclose()


def create_client(
    app: FastAPI,
) -> AsyncClient:
    """Return a new http test client to the app."""

    transport = ASGIWebSocketTransport(
        app=app,
        root_path="/api",
    )

    return AsyncClient(
        base_url=f"https://{app.state.config.host_name}",
        transport=transport,
    )


async def login_as_user(
    client: AsyncClient,
    username: str,
    password: str,
) -> AsyncClient:
    """Login with `client` using `username` and `password`."""

    resp = await client.post(
        "/api/v1/auth/login",
        data={
            "grant_type": "password",
            "username": username,
            "password": password,
        },
    )
    resp.raise_for_status()

    return client
