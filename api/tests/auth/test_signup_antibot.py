import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.user.models import User
from babytroc.routers.v1.auth.new import rate_limit_signup

VALID = {
    "name": "newperson",
    "email": "newperson@example.com",
    "password": "Pa55word42",
    "cap_token": "valid",
}


def _payload(**overrides) -> dict:
    return {**VALID, **overrides}


async def _count_users(database_sessionmaker: async_sessionmaker) -> int:
    async with database_sessionmaker() as db:
        result = await db.execute(select(User))
        return len(result.scalars().all())


async def test_happy_path_creates_user(
    client: AsyncClient,
    database_sessionmaker: async_sessionmaker,
):
    before = await _count_users(database_sessionmaker)
    resp = await client.post("/api/v1/auth/new", json=_payload())
    assert resp.is_success, resp.text
    after = await _count_users(database_sessionmaker)
    assert after == before + 1


async def test_honeypot_rejects_with_400_invalid_submission(
    client: AsyncClient,
    database_sessionmaker: async_sessionmaker,
):
    before = await _count_users(database_sessionmaker)
    resp = await client.post(
        "/api/v1/auth/new", json=_payload(website="bot was here"),
    )
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"
    after = await _count_users(database_sessionmaker)
    assert after == before


@pytest.mark.parametrize("cap_verify_result", [False])
async def test_cap_rejected_returns_400_invalid_submission(
    client: AsyncClient,
    database_sessionmaker: async_sessionmaker,
    cap_verify_result: bool,
):
    before = await _count_users(database_sessionmaker)
    resp = await client.post("/api/v1/auth/new", json=_payload())
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"
    after = await _count_users(database_sessionmaker)
    assert after == before


async def test_rate_limit_anon_returns_429(
    client: AsyncClient,
    database_sessionmaker: async_sessionmaker,
    tight_rate_limit_factory,
):
    tight_rate_limit_factory(
        dep=rate_limit_signup,
        key_prefix="signup-test",
        anon_limit=2, auth_limit=2, window_seconds=60,
    )
    r1 = await client.post("/api/v1/auth/new", json=_payload(name="Person Alpha", email="a@a.com"))
    r2 = await client.post("/api/v1/auth/new", json=_payload(name="Person Beta", email="b@b.com"))
    assert r1.is_success, r1.text
    assert r2.is_success, r2.text
    r3 = await client.post("/api/v1/auth/new", json=_payload(name="Person Gamma", email="c@c.com"))
    assert r3.status_code == 429
