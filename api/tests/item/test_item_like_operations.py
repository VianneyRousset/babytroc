from httpx import AsyncClient

from babytroc.domains.item.schemas.read import ItemRead


class TestItemLikeOperations:
    """Test like/unlike operations and counts."""

    async def test_like_item_and_count(
        self,
        bob_client: AsyncClient,
        alice_items: list[ItemRead],
    ):
        """Like an item, verify it appears in liked list and likes_count increments."""
        item = alice_items[0]

        # get initial likes count
        resp = await bob_client.get(f"/api/v1/items/{item.id}")
        resp.raise_for_status()
        initial_likes = resp.json()["likes_count"]

        # like it
        resp = await bob_client.post(f"/api/v1/me/liked/{item.id}")
        resp.raise_for_status()

        # verify in liked list
        resp = await bob_client.get("/api/v1/me/liked")
        resp.raise_for_status()
        liked_ids = [i["id"] for i in resp.json()]
        assert item.id in liked_ids

        # verify likes_count incremented
        resp = await bob_client.get(f"/api/v1/items/{item.id}")
        resp.raise_for_status()
        assert resp.json()["likes_count"] == initial_likes + 1

    async def test_unlike_item_and_count(
        self,
        carol_client: AsyncClient,
        alice_items: list[ItemRead],
    ):
        """Like then unlike, verify removed and count decrements."""
        item = alice_items[0]

        # like
        resp = await carol_client.post(f"/api/v1/me/liked/{item.id}")
        resp.raise_for_status()

        # get count after like
        resp = await carol_client.get(f"/api/v1/items/{item.id}")
        resp.raise_for_status()
        count_after_like = resp.json()["likes_count"]

        # unlike
        resp = await carol_client.delete(f"/api/v1/me/liked/{item.id}")
        resp.raise_for_status()

        # verify removed from list
        resp = await carol_client.get("/api/v1/me/liked")
        resp.raise_for_status()
        liked_ids = [i["id"] for i in resp.json()]
        assert item.id not in liked_ids

        # verify count decremented
        resp = await carol_client.get(f"/api/v1/items/{item.id}")
        resp.raise_for_status()
        assert resp.json()["likes_count"] == count_after_like - 1

    # NOTE: GET /me/liked/{item_id} triggers a SQLAlchemy auto-correlation
    # error with the deferred likes_count column property. This is a
    # pre-existing bug to fix separately.
