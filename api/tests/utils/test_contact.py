from email.message import Message

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from babytroc.domains.user.schemas.private import UserPrivateRead

VALID_PAYLOAD = {
    "name": "Alice",
    "email": "alice@example.com",
    "subject": "Hello",
    "message": "Hi there",
    "cap_token": "valid-token",
}


def _payload(**overrides) -> dict:
    return {**VALID_PAYLOAD, **overrides}


def _html_body(msg: Message) -> str:
    """Extract the text/html part of a fastapi-mail recorded message."""
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            payload = part.get_payload(decode=True)
            assert isinstance(payload, bytes)
            charset = part.get_content_charset() or "utf-8"
            return payload.decode(charset)
    err = "no text/html part found"
    raise AssertionError(err)


# ---- happy paths ----

async def test_anon_valid_submission_returns_204(client: AsyncClient, app: FastAPI):
    with app.state.email_client.record_messages() as outbox:
        resp = await client.post("/api/v1/utils/contact", json=_payload())
    assert resp.status_code == 204
    assert len(outbox) == 1
    assert "test-contact@babytroc.ch" in outbox[0]["To"]
    body = _html_body(outbox[0])
    assert "Authenticated user ID:</b> —" in body


async def test_authenticated_submission_includes_user_id(
    alice_client: AsyncClient,
    app: FastAPI,
    alice: UserPrivateRead,
):
    with app.state.email_client.record_messages() as outbox:
        resp = await alice_client.post("/api/v1/utils/contact", json=_payload())
    assert resp.status_code == 204
    body = _html_body(outbox[0])
    assert f"Authenticated user ID:</b> {alice.id}" in body


# ---- honeypot ----

async def test_honeypot_filled_returns_400_invalid_submission(
    client: AsyncClient, app: FastAPI
):
    with app.state.email_client.record_messages() as outbox:
        resp = await client.post(
            "/api/v1/utils/contact", json=_payload(website="bot was here"),
        )
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"
    assert outbox == []


# ---- cap layer ----

@pytest.mark.parametrize("cap_verify_result", [False])
async def test_cap_rejected_returns_400_invalid_submission(
    client: AsyncClient, app: FastAPI, cap_verify_result
):
    with app.state.email_client.record_messages() as outbox:
        resp = await client.post("/api/v1/utils/contact", json=_payload())
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"
    assert outbox == []


@pytest.mark.parametrize("cap_verify_raises", [True])
async def test_cap_unreachable_returns_400_invalid_submission(
    client: AsyncClient, app: FastAPI, cap_verify_raises
):
    with app.state.email_client.record_messages() as outbox:
        resp = await client.post("/api/v1/utils/contact", json=_payload())
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"
    assert outbox == []


# ---- rate limit ----

async def test_anon_rate_limit_triggers_429(
    client: AsyncClient, tight_rate_limit_factory
):
    tight_rate_limit_factory(anon_limit=2, auth_limit=10, window_seconds=60)
    r1 = await client.post("/api/v1/utils/contact", json=_payload())
    r2 = await client.post("/api/v1/utils/contact", json=_payload())
    r3 = await client.post("/api/v1/utils/contact", json=_payload())
    assert r1.status_code == 204
    assert r2.status_code == 204
    assert r3.status_code == 429
    assert r3.json()["message"] == "RATE_LIMITED"


async def test_auth_rate_limit_triggers_429(
    alice_client: AsyncClient, tight_rate_limit_factory
):
    tight_rate_limit_factory(anon_limit=10, auth_limit=2, window_seconds=60)
    r1 = await alice_client.post("/api/v1/utils/contact", json=_payload())
    r2 = await alice_client.post("/api/v1/utils/contact", json=_payload())
    r3 = await alice_client.post("/api/v1/utils/contact", json=_payload())
    assert r1.status_code == 204
    assert r2.status_code == 204
    assert r3.status_code == 429


async def test_anon_and_auth_quotas_are_isolated(
    client: AsyncClient,
    alice_client: AsyncClient,
    tight_rate_limit_factory,
):
    tight_rate_limit_factory(anon_limit=2, auth_limit=2, window_seconds=60)
    # Use up alice's quota
    r1 = await alice_client.post("/api/v1/utils/contact", json=_payload())
    r2 = await alice_client.post("/api/v1/utils/contact", json=_payload())
    assert r1.status_code == 204
    assert r2.status_code == 204
    # Anonymous client on same IP should still have its full quota
    r3 = await client.post("/api/v1/utils/contact", json=_payload())
    r4 = await client.post("/api/v1/utils/contact", json=_payload())
    assert r3.status_code == 204
    assert r4.status_code == 204


# ---- pydantic validation ----

@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("name", ""),
        ("name", "x" * 101),
        ("email", "not-an-email"),
        ("subject", ""),
        ("subject", "x" * 201),
        ("message", ""),
        ("message", "x" * 5001),
    ],
)
async def test_validation_rejects_bad_field(
    client: AsyncClient, field: str, bad_value: str
):
    resp = await client.post(
        "/api/v1/utils/contact", json=_payload(**{field: bad_value}),
    )
    # The app's RequestValidationError handler converts 422 to 400 with detail.
    assert resp.status_code == 400


async def test_validation_rejects_missing_field(client: AsyncClient):
    payload = _payload()
    payload.pop("cap_token")
    resp = await client.post("/api/v1/utils/contact", json=payload)
    assert resp.status_code == 400


# ---- HTML injection safety (also covered at sender unit level) ----

async def test_html_injection_in_message_is_escaped(
    client: AsyncClient, app: FastAPI
):
    with app.state.email_client.record_messages() as outbox:
        resp = await client.post(
            "/api/v1/utils/contact",
            json=_payload(message="<script>alert(1)</script>"),
        )
    assert resp.status_code == 204
    body = _html_body(outbox[0])
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body
