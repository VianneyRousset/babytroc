from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import jwt
import pytest
from fastapi import status
from httpx_ws import aconnect_ws

from app.domains.auth.schemas.availability import AuthAccountAvailability
from app.domains.chat.schemas.websocket import WebsocketMessageUpdatedAccountValidation
from app.domains.auth.services.refresh_token import list_account_password_reset_authorizations
from app.domains.user.services import get_user_validation_code_by_email
from tests.fixtures.clients import create_client
from tests.fixtures.websockets import WebSocketRecorder

if TYPE_CHECKING:
    from httpx import AsyncClient
    from httpx_ws import AsyncWebSocketSession
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from tests.fixtures.users import UserData


@pytest.mark.usefixtures("alice")
class TestAuthLogin:
    """Test auth endpoints related to login and logout."""

    async def test_access_denied(
        self,
        client: AsyncClient,
    ):
        """Check that GET /v1/me return 401 UNAUTHORIZED"""
        resp = await client.get("/api/v1/me")

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_wrong_email(
        self,
        client: AsyncClient,
        alice_user_data: UserData,
    ):
        """Check that login with a wrong email return 401 UNAUTHORIZED."""

        resp = await client.post(
            "/api/v1/auth/login",
            data={
                "grant_type": "password",
                "username": "wrong_email",
                "password": alice_user_data["password"],
            },
        )

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_wrong_password(
        self,
        client: AsyncClient,
        alice_user_data: UserData,
    ):
        """Check that login with a wrong password return 401 UNAUTHORIZED."""

        resp = await client.post(
            "/api/v1/auth/login",
            data={
                "grant_type": "password",
                "username": alice_user_data["email"],
                "password": "wrong_password",
            },
        )

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_access_token(
        self,
        client: AsyncClient,
        alice_user_data: UserData,
    ):
        """Check that login returns a valid access token."""

        resp = await client.post(
            "/api/v1/auth/login",
            data={
                "grant_type": "password",
                "username": alice_user_data["email"],
                "password": alice_user_data["password"],
            },
        )
        resp.raise_for_status()
        assert resp.json()["validated"]

        (await client.get("/api/v1/me")).raise_for_status()

    async def test_refresh_token(
        self,
        alice_client: AsyncClient,
    ):
        """Check that credentials can be renewed."""

        resp = await alice_client.post("/api/v1/auth/refresh")
        resp.raise_for_status()
        assert resp.json()["validated"]

        (await alice_client.get("/api/v1/me")).raise_for_status()

    async def test_logout(
        self,
        alice_client: AsyncClient,
    ):
        """Check logout removes credentials."""

        resp = await alice_client.post("/api/v1/auth/logout")
        resp.raise_for_status()

        resp = await alice_client.get("/api/v1/me")
        assert not resp.is_success


@pytest.mark.usefixtures("alice")
class TestAuthNewAccount:
    """Test auth endpoints related to account creation."""

    async def test_create_account(
        self,
        app_config,
        client: AsyncClient,
        app,
        database_sessionmaker: async_sessionmaker,
    ):
        """Check that a new account can be created and validated."""

        email = "ojownlydifctujhohfzresasqaxe@hcycjxybfvvnfkbapireyezpxnt.com"
        password = "xxxXXX42"

        # check forbidden access
        resp = await client.get("/api/v1/me")
        assert not resp.is_success

        # create account
        resp = await client.post(
            "/api/v1/auth/new",
            json={
                "name": "newaccount",
                "email": email,
                "password": password,
            },
        )
        resp.raise_for_status()

        # check the account is not validated yet
        assert not resp.json()["validated"]

        # check still forbidden access
        resp = await client.get("/api/v1/me")
        assert not resp.is_success

        # check can resend email
        (await client.post("/api/v1/auth/resend-validation-email")).raise_for_status()

        # get validation code
        async with database_sessionmaker.begin() as db:
            validation_code = await get_user_validation_code_by_email(
                db=db,
                email=email,
            )

        # should be logged into the invalidated account and thus access
        # the websocket — need a separate entered client for websocket
        ws_client = create_client(app)
        await ws_client.__aenter__()
        ws_client.cookies = client.cookies

        websocket: AsyncWebSocketSession
        async with aconnect_ws("/api/v1/me/websocket", ws_client) as websocket:
            websocket_recorder = WebSocketRecorder(websocket)

            async with websocket_recorder:
                # validate account
                client_for_validation = create_client(app)
                resp = await client_for_validation.post(
                    f"/api/v1/auth/validate/{validation_code}"
                )
                resp.raise_for_status()

        # check received a notification
        assert isinstance(
            websocket_recorder.message, WebsocketMessageUpdatedAccountValidation
        )
        assert websocket_recorder.message.validated

        # refresh token
        resp = await client.post("/api/v1/auth/refresh")
        resp.raise_for_status()

        # check the account is now validated
        assert resp.json()["validated"]

        # check access granted
        resp = await client.get("/api/v1/me")
        resp.raise_for_status()

    @pytest.mark.parametrize(
        ("name", "email", "expected_result"),
        [
            ("alice", None, False),
            (None, "alice@babytroc.ch", False),
            ("uicwdntnjrdscndphwspcskgjxoduwyq", None, True),
            (None, "qeuupfnlbombnsmk@lzlgzoynvwwaiwnz.com", True),
        ],
    )
    async def test_account_availability(
        self,
        client: AsyncClient,
        alice_user_data: UserData,
        name: str | None,
        email: str | None,
        expected_result: bool,
    ):
        """Check if account availability is correct."""

        params = {}
        if name:
            params["name"] = name
        if email:
            params["email"] = email

        resp = await client.get(
            "/api/v1/auth/available",
            params=params,
        )
        resp.raise_for_status()
        availability = AuthAccountAvailability.model_validate(resp.json())
        assert availability.available == expected_result

    @pytest.mark.parametrize(
        ("name", "email", "password"),
        [
            ("", "alice@babytroc.ch", "xxxXXX42"),
            ("a" * 2, "alice@babytroc.ch", "xxxXXX42"),
            ("w.w", "alice@babytroc.ch", "xxxXXX42"),
            ("-alice-", "alice@babytroc.ch", "xxxXXX42"),
            ("a" * 31, "alice@babytroc.ch", "xxxXXX42"),
            ("alice", "ali@woij", "xxxXXX42"),
            ("alice", "alice@babytroc.ch", "xX1"),
            ("alice", "alice@babytroc.ch", "abcabc1"),
            ("alice", "alice@babytroc.ch", "ABCABC1"),
            ("alice", "alice@babytroc.ch", "abcABCD"),
        ],
    )
    async def test_create_account_invalid(
        self,
        client: AsyncClient,
        name: str,
        email: str,
        password: str,
    ):
        """Check that a new account cannot be created if a field is invalid."""

        resp = await client.post(
            "/api/v1/auth/new",
            json={
                "name": name,
                "email": email,
                "password": password,
            },
        )
        assert not resp.is_success


@pytest.mark.usefixtures("alice", "bob")
class TestAuthPasswordReset:
    """Test auth endpoints related to account password reset."""

    async def test_password_reset(
        self,
        database_sessionmaker: async_sessionmaker,
        client: AsyncClient,
        alice_user_data: UserData,
    ):
        """Check that a new account can be created and validated."""

        new_password = "newPassword42"

        # login should fail
        resp = await client.post(
            "/api/v1/auth/login",
            data={
                "grant_type": "password",
                "username": alice_user_data["email"],
                "password": new_password,
            },
        )
        assert not resp.is_success

        # create account password reset authorization
        resp = await client.post(
            "/api/v1/auth/reset-password",
            json={"email": alice_user_data["email"]},
        )
        resp.raise_for_status()

        # get authorization code manually
        async with database_sessionmaker.begin() as db:
            authorizations = await list_account_password_reset_authorizations(db)
            authorization_code = authorizations[0].authorization_code

        # apply account password reset
        (
            await client.post(
                f"/api/v1/auth/reset-password/{authorization_code}",
                json={"password": new_password},
            )
        ).raise_for_status()

        # shouldn't be able to reuse account password reset authorization_code
        resp = await client.post(
            f"/api/v1/auth/reset-password/{authorization_code}",
            json={"password": "mxgahflnggmfujas"},
        )
        assert not resp.is_success

        # login should now succeed
        (
            await client.post(
                "/api/v1/auth/login",
                data={
                    "grant_type": "password",
                    "username": alice_user_data["email"],
                    "password": new_password,
                },
            )
        ).raise_for_status()

    async def test_password_reset_wrong_email(
        self,
        client: AsyncClient,
    ):
        """Password reset on an non-existing email should return 404."""

        resp = await client.post(
            "/api/v1/auth/reset-password",
            json={"email": "ilxkndknnegikahj@artuxmjklwovtrrk.com"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize("new_password", ["xX1", "abcabc1", "ABCABC1", "abcABCD"])
    async def test_password_reset_invalid(
        self,
        database_sessionmaker: async_sessionmaker,
        client: AsyncClient,
        bob_user_data: UserData,
        new_password: str,
    ):
        """Password reset with invalid password should fail."""

        # create account password reset authorization
        resp = await client.post(
            "/api/v1/auth/reset-password",
            json={"email": bob_user_data["email"]},
        )
        resp.raise_for_status()

        # get authorization code manually
        async with database_sessionmaker.begin() as db:
            authorizations = await list_account_password_reset_authorizations(db)
            authorization_code = authorizations[0].authorization_code

        # apply account password reset
        resp = await client.post(
            f"/api/v1/auth/reset-password/{authorization_code}",
            json={"password": new_password},
        )
        assert not resp.is_success


@pytest.mark.usefixtures("alice")
class TestAuthTokenEdgeCases:
    """Test token validation edge cases."""

    async def test_expired_access_token(
        self,
        client: AsyncClient,
        app_config,
    ):
        """Expired JWT should return 401."""
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
        resp = await client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_malformed_jwt(
        self,
        client: AsyncClient,
    ):
        """Garbage Bearer token should return 401."""
        resp = await client.get(
            "/api/v1/me",
            headers={"Authorization": "Bearer not.a.valid.jwt"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_bad_signature_jwt(
        self,
        client: AsyncClient,
        app_config,
    ):
        """JWT signed with wrong key should return 401."""
        bad_token = jwt.encode(
            {
                "iat": datetime.now(UTC),
                "exp": datetime.now(UTC) + timedelta(hours=1),
                "sub": "1",
                "validated": True,
            },
            key="wrong-secret-key",
            algorithm=app_config.auth.algorithm,
        )
        resp = await client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {bad_token}"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
