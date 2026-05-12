import pytest
from httpx import AsyncClient

from babytroc.domains.user.schemas.private import UserPrivateRead
from babytroc.routers.v1.auth.reset import rate_limit_password_reset


def _payload(*, email: str, **overrides) -> dict:
    return {"email": email, "cap_token": "valid", **overrides}


async def test_happy_path_returns_success(client: AsyncClient, alice: UserPrivateRead):
    resp = await client.post(
        "/api/v1/auth/reset-password", json=_payload(email=alice.email),
    )
    assert resp.is_success, resp.text


async def test_honeypot_returns_400_invalid_submission(
    client: AsyncClient, alice: UserPrivateRead,
):
    resp = await client.post(
        "/api/v1/auth/reset-password",
        json=_payload(email=alice.email, website="x"),
    )
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"


@pytest.mark.parametrize("cap_verify_result", [False])
async def test_cap_rejected_returns_400(
    client: AsyncClient, alice: UserPrivateRead, cap_verify_result: bool,
):
    resp = await client.post(
        "/api/v1/auth/reset-password", json=_payload(email=alice.email),
    )
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"


async def test_rate_limit_anon_returns_429(
    client: AsyncClient, alice: UserPrivateRead, tight_rate_limit_factory,
):
    tight_rate_limit_factory(
        dep=rate_limit_password_reset,
        key_prefix="password-reset-test",
        anon_limit=1, auth_limit=1, window_seconds=60,
    )
    r1 = await client.post(
        "/api/v1/auth/reset-password", json=_payload(email=alice.email),
    )
    assert r1.is_success, r1.text
    r2 = await client.post(
        "/api/v1/auth/reset-password", json=_payload(email=alice.email),
    )
    assert r2.status_code == 429
