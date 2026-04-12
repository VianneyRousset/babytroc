from fastapi import status
from httpx import AsyncClient

from app.schemas.item.read import ItemRead


class TestItemSave:
    """Test saved items CRUD."""

    async def test_save_and_list(
        self,
        alice_client: AsyncClient,
        alice_items: list[ItemRead],
    ):
        """Save an item and verify it appears in saved list."""
        item = alice_items[0]

        resp = await alice_client.post(f"/api/v1/me/saved/{item.id}")
        resp.raise_for_status()

        resp = await alice_client.get("/api/v1/me/saved")
        resp.raise_for_status()
        saved_ids = [i["id"] for i in resp.json()]
        assert item.id in saved_ids

    async def test_save_and_get(
        self,
        bob_client: AsyncClient,
        alice_items: list[ItemRead],
    ):
        """Save an item and verify GET /me/saved/{item_id} returns it."""
        item = alice_items[0]

        resp = await bob_client.post(f"/api/v1/me/saved/{item.id}")
        resp.raise_for_status()

        resp = await bob_client.get(f"/api/v1/me/saved/{item.id}")
        resp.raise_for_status()
        assert resp.json()["id"] == item.id

    async def test_save_and_unsave(
        self,
        bob_client: AsyncClient,
        bob_items: list[ItemRead],
    ):
        """Save then unsave an item, verify it disappears."""
        item = bob_items[0]

        resp = await bob_client.post(f"/api/v1/me/saved/{item.id}")
        resp.raise_for_status()

        resp = await bob_client.delete(f"/api/v1/me/saved/{item.id}")
        resp.raise_for_status()

        resp = await bob_client.get("/api/v1/me/saved")
        resp.raise_for_status()
        saved_ids = [i["id"] for i in resp.json()]
        assert item.id not in saved_ids

    async def test_unsave_non_saved_item(
        self,
        carol_client: AsyncClient,
        alice_items: list[ItemRead],
    ):
        """Unsaving a non-saved item succeeds (idempotent delete)."""
        item = alice_items[0]
        resp = await carol_client.delete(f"/api/v1/me/saved/{item.id}")
        # service is idempotent
        resp.raise_for_status()
