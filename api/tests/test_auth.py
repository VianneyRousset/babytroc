from fastapi import status
from fastapi.testclient import TestClient


def test_access_denied(
    client: TestClient,
):
    """Check that GET /v1/me return 401 UNAUTHORIZED"""
    resp = client.get("/v1/me")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_wrong_email(
    client: TestClient,
    users: list[int],
    users_data: list[dict],
):
    """Check that login with a wrong email return 401 UNAUTHORIZED."""

    # login
    resp = client.post(
        "/v1/auth/login",
        data={
            "grant_type": "password",
            "username": "wrong_email",
            "password": users_data[0]["password"],
        },
    )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_wrong_password(
    client: TestClient,
    users: list[int],
    users_data: list[dict],
):
    """Check that login with a wrong password return 401 UNAUTHORIZED."""

    # login
    resp = client.post(
        "/v1/auth/login",
        data={
            "grant_type": "password",
            "username": users_data[0]["email"],
            "password": "wrong_password",
        },
    )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_access_token(
    client: TestClient,
    users: list[int],
    users_data: list[dict],
):
    """Check that login returns a valid access token."""

    # login
    client.post(
        "/v1/auth/login",
        data={
            "grant_type": "password",
            "username": users_data[0]["email"],
            "password": users_data[0]["password"],
        },
    ).raise_for_status()

    client.get("/v1/me").raise_for_status()


def test_refresh_token(
    client0: TestClient,
):
    """Check that credentials can be renewed."""

    # refresh
    resp = client0.post("/v1/auth/refresh")
    resp.raise_for_status()

    # test access is wokring
    client0.get("/v1/me").raise_for_status()
