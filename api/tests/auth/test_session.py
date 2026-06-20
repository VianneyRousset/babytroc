from httpx import AsyncClient


async def test_logged_in_client_returns_true(alice_client: AsyncClient):
    resp = await alice_client.get("/api/v1/auth/session")
    assert resp.is_success, resp.text
    assert resp.status_code == 200
    assert resp.json() == {"logged_in": True}


async def test_anonymous_client_returns_false(client: AsyncClient):
    resp = await client.get("/api/v1/auth/session")
    assert resp.is_success, resp.text
    assert resp.status_code == 200
    assert resp.json() == {"logged_in": False}


async def test_garbage_token_returns_false(client: AsyncClient):
    resp = await client.get(
        "/api/v1/auth/session",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.is_success, resp.text
    assert resp.status_code == 200
    assert resp.json() == {"logged_in": False}
