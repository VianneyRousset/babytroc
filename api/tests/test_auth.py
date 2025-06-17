import pytest
import sqlalchemy
from fastapi import status
from fastapi.testclient import TestClient

from app.clients.database.auth import list_account_password_reset_authorizations
from app.clients.database.user import get_user_by_email
from app.config import Config
from app.schemas.auth.availability import AuthAccountAvailability
from app.schemas.user.private import UserPrivateRead
from app.schemas.websocket import WebsocketMessageUpdatedAccountValidation
from tests.fixtures.clients import create_client
from tests.fixtures.users import UserData
from tests.fixtures.websockets import WebSocketRecorder


@pytest.mark.usefixtures("alice")
class TestAuthLogin:
    """Test auth endpoints related to login and logout."""

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
        resp = client.post(
            "/v1/auth/login",
            data={
                "grant_type": "password",
                "username": alice_user_data["email"],
                "password": alice_user_data["password"],
            },
        )
        resp.raise_for_status()
        assert resp.json()["validated"]

        client.get("/v1/me").raise_for_status()

    def test_refresh_token(
        self,
        alice_client: TestClient,
    ):
        """Check that credentials can be renewed."""

        # refresh
        resp = alice_client.post("/v1/auth/refresh")
        resp.raise_for_status()
        assert resp.json()["validated"]

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


@pytest.mark.usefixtures("alice")
class TestAuthNewAccount:
    """Test auth endpoints related to account creation."""

    def test_create_account(
        self,
        app_config: Config,
        client: TestClient,
        database: sqlalchemy.URL,
    ):
        """Check that a new account can be created and validated."""

        email = "ojownlydifctujhohfzresasqaxe@hcycjxybfvvnfkbapireyezpxnt.com"
        password = "xxxXXX42"  # noqa: S105

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

        # check the account is not validated yet
        assert not resp.json()["validated"]

        # check still forbidden access
        resp = client.get("/v1/me")
        assert not resp.is_success

        # check can resend email
        client.post("/v1/auth/resend-validation-email").raise_for_status()

        # get validation code
        engine = sqlalchemy.create_engine(database)
        with sqlalchemy.orm.Session(engine) as db, db.begin():
            user = get_user_by_email(
                db=db,
                email=email,
            )
            validation_code = user.validation_code

        # should be logged into the invalidated account and thus access
        # the websocket

        websocket = client.websocket_connect("/v1/me/websocket")
        websocket_recorder = WebSocketRecorder(websocket)

        with websocket_recorder:
            # validate for validation
            with create_client(app_config) as client_for_validation:
                client_for_validation.post(
                    f"/v1/auth/validate/{validation_code}"
                ).raise_for_status()

        # check received a notification
        assert isinstance(
            websocket_recorder.message, WebsocketMessageUpdatedAccountValidation
        )
        assert websocket_recorder.message.validated

        # refresh token
        resp = client.post("/v1/auth/refresh")
        resp.raise_for_status()

        # check the account is now validated
        assert resp.json()["validated"]

        # check access granted
        resp = client.get("/v1/me")
        print(resp.text)
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
    def test_account_availability(
        self,
        client: TestClient,
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

        # check alice's name is not available
        resp = client.get(
            "v1/auth/available",
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
    def test_create_account_invalid(
        self,
        client: TestClient,
        name: str,
        email: str,
        password: str,
    ):
        """Check that a new account cannot be created if a field is invalid."""

        # create account
        resp = client.post(
            "/v1/auth/new",
            json={
                "name": name,
                "email": email,
                "password": password,
            },
        )
        print(resp.text)
        assert not resp.is_success


@pytest.mark.usefixtures("alice", "bob")
class TestAuthPasswordReset:
    """Test auth endpoints related to account password reset."""

    def test_password_reset(
        self,
        database: sqlalchemy.URL,
        client: TestClient,
        alice_user_data: UserData,
    ):
        """Check that a new account can be created and validated."""

        new_password = "newPassword42"  # noqa: S105

        # login should fail
        resp = client.post(
            "/v1/auth/login",
            data={
                "grant_type": "password",
                "username": alice_user_data["email"],
                "password": new_password,
            },
        )
        assert not resp.is_success

        # create account password reset authorization
        resp = client.post(
            "/v1/auth/reset-password",
            json={"email": alice_user_data["email"]},
        )
        print(resp.text)
        resp.raise_for_status()

        # get authorization code manually
        engine = sqlalchemy.create_engine(database)
        with sqlalchemy.orm.Session(engine) as db, db.begin():
            authorizations = list_account_password_reset_authorizations(db)
            authorization_code = authorizations[0].authorization_code

        # apply account password reset
        client.post(
            f"/v1/auth/reset-password/{authorization_code}",
            json={"password": new_password},
        ).raise_for_status()

        # shouldn't be able to reuse account password reset authorization_code
        resp = client.post(
            f"/v1/auth/reset-password/{authorization_code}",
            json={"password": "mxgahflnggmfujas"},
        )
        assert not resp.is_success

        # login should now succeed
        client.post(
            "/v1/auth/login",
            data={
                "grant_type": "password",
                "username": alice_user_data["email"],
                "password": new_password,
            },
        ).raise_for_status()

    def test_password_reset_wrong_email(
        self,
        client: TestClient,
    ):
        """Password reset on an non-existing email should return 404."""

        resp = client.post(
            "/v1/auth/reset-password",
            json={"email": "ilxkndknnegikahj@artuxmjklwovtrrk.com"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize("new_password", ["xX1", "abcabc1", "ABCABC1", "abcABCD"])
    def test_password_reset_invalid(
        self,
        database: sqlalchemy.URL,
        client: TestClient,
        bob_user_data: UserData,
        new_password: str,
    ):
        """Password reset with invalid password should fail."""

        # create account password reset authorization
        resp = client.post(
            "/v1/auth/reset-password",
            json={"email": bob_user_data["email"]},
        )
        print(resp.text)
        resp.raise_for_status()

        # get authorization code manually
        engine = sqlalchemy.create_engine(database)
        with sqlalchemy.orm.Session(engine) as db, db.begin():
            authorizations = list_account_password_reset_authorizations(db)
            authorization_code = authorizations[0].authorization_code

        # apply account password reset
        resp = client.post(
            f"/v1/auth/reset-password/{authorization_code}",
            json={"password": new_password},
        )
        assert not resp.is_success
