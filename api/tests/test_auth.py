import pytest
from fastapi import status
from fastapi.testclient import TestClient

from tests.fixtures.users import UserData


@pytest.mark.usefixtures("database", "alice")
class TestAuth:
    """Test auth endpoints."""

    def test_access_denied(
        self,
        client: TestClient,
    ):
        """Check that GET /v1/me return 401 UNAUTHORIZED"""
        resp = client.get("/v1/me")

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_wrong_email(
        self,
        client: TestClient,
        alice_user_data: UserData,
    ):
        """Check that login with a wrong email return 401 UNAUTHORIZED."""

        # login
        resp = client.post(
            "/v1/auth/login",
            data={
                "grant_type": "password",
                "username": "wrong_email",
                "password": alice_user_data["password"],
            },
        )

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_wrong_password(
        self,
        client: TestClient,
        alice_user_data: UserData,
    ):
        """Check that login with a wrong password return 401 UNAUTHORIZED."""

        # login
        resp = client.post(
            "/v1/auth/login",
            data={
                "grant_type": "password",
                "username": alice_user_data["email"],
                "password": "wrong_password",
            },
        )

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_access_token(
        self,
        client: TestClient,
        alice_user_data: UserData,
    ):
        """Check that login returns a valid access token."""

        # login
        client.post(
            "/v1/auth/login",
            data={
                "grant_type": "password",
                "username": alice_user_data["email"],
                "password": alice_user_data["password"],
            },
        ).raise_for_status()

        client.get("/v1/me").raise_for_status()

    def test_refresh_token(
        self,
        alice_client: TestClient,
    ):
        """Check that credentials can be renewed."""

        # refresh
        resp = alice_client.post("/v1/auth/refresh")
        resp.raise_for_status()

        # test access is wokring
        alice_client.get("/v1/me").raise_for_status()
