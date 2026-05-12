import pytest
from httpx import AsyncClient

from babytroc.routers.v1.me.items.create import rate_limit_item_create
from tests.fixtures.items import ItemData


async def test_happy_path_creates_item(
    alice_client: AsyncClient,
    alice_new_item_data: ItemData,
):
    resp = await alice_client.post(
        "/api/v1/me/items", json=alice_new_item_data,
    )
    assert resp.status_code == 201, resp.text


async def test_honeypot_rejects_with_400(
    alice_client: AsyncClient,
    alice_new_item_data: ItemData,
):
    body = {**alice_new_item_data, "website": "x"}
    resp = await alice_client.post("/api/v1/me/items", json=body)
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"


@pytest.mark.parametrize("cap_verify_result", [False])
async def test_cap_rejected_returns_400(
    alice_client: AsyncClient,
    alice_new_item_data: ItemData,
    cap_verify_result: bool,
):
    resp = await alice_client.post("/api/v1/me/items", json=alice_new_item_data)
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"


async def test_rate_limit_auth_returns_429(
    alice_client: AsyncClient,
    alice_new_item_data: ItemData,
    tight_rate_limit_factory,
):
    tight_rate_limit_factory(
        dep=rate_limit_item_create,
        key_prefix="item-create-test",
        anon_limit=2, auth_limit=2, window_seconds=60,
    )
    r1 = await alice_client.post("/api/v1/me/items", json=alice_new_item_data)
    r2 = await alice_client.post("/api/v1/me/items", json=alice_new_item_data)
    r3 = await alice_client.post("/api/v1/me/items", json=alice_new_item_data)
    assert r1.status_code == 201, r1.text
    assert r2.status_code == 201, r2.text
    assert r3.status_code == 429
