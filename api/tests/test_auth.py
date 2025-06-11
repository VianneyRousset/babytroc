import pytest
import sqlalchemy
from fastapi import status
from fastapi.testclient import TestClient

from app.clients.database.user import get_user_by_email
from tests.fixtures.users import UserData


@pytest.mark.usefixtures("alice")
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

    def test_logout(
        self,
        alice_client: TestClient,
    ):
        """Check logout removes credentials."""

        # logout
        resp = alice_client.post("/v1/auth/logout")
        resp.raise_for_status()

        # test access is not working anymore
        resp = alice_client.get("/v1/me")
        assert not resp.is_success

    def test_new_account(
        self,
        client: TestClient,
        database: sqlalchemy.URL,
    ):
        """Check that a new account can be created and validated."""

        email = "ojownlydifctujhohfzresasqaxe@hcycjxybfvvnfkbapireyezpxnt.com"
        password = "xxx"  # noqa: S105

        # check forbidden access
        resp = client.get("/v1/me")
        assert not resp.is_success

        # create account
        resp = client.post(
            "/v1/auth/new",
            json={
                "name": "newaccount",
                "email": email,
                "password": password,
            },
        )
        print(resp.text)
        resp.raise_for_status()

        # login
        client.post(
            "/v1/auth/login",
            data={
                "grant_type": "password",
                "username": email,
                "password": password,
            },
        ).raise_for_status()

        # check still forbidden access
        resp = client.get("/v1/me")
        assert not resp.is_success

        # check can resend email
        client.post("/v1/auth/resend-validation-email").raise_for_status()

        # get validation code
        engine = sqlalchemy.create_engine(database)
        with sqlalchemy.orm.Session(engine) as db, db.begin():
            validation_code = get_user_by_email(
                db=db,
                email=email,
            )

        # validate
        client.post(f"/v1/auth/validate/{validation_code}").raise_for_status()

        # refresh token
        client.post("/v1/auth/refresh").raise_for_status()

        # check access granted
        resp = client.get("/v1/me")
        assert not resp.is_success
