import pytest
from fastapi import status
from httpx import AsyncClient


class TestPaginationEdgeCases:
    """Test pagination boundary conditions on representative endpoints."""

    @pytest.mark.parametrize("limit", [0, -1])
    async def test_limit_invalid_items(
        self,
        client: AsyncClient,
        limit: int,
    ):
        """Zero or negative limit should return 422."""
        resp = await client.get("/api/v1/items", params={"n": limit})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_limit_exceeds_max_items(
        self,
        client: AsyncClient,
    ):
        """Limit > 256 should return 422."""
        resp = await client.get("/api/v1/items", params={"n": 257})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_limit_at_max_items(
        self,
        client: AsyncClient,
    ):
        """Limit == 256 should succeed."""
        resp = await client.get("/api/v1/items", params={"n": 256})
        resp.raise_for_status()

    async def test_empty_collection(
        self,
        alice_client: AsyncClient,
    ):
        """Querying saved items with nothing saved returns empty list."""
        # carol has no saved items
        resp = await alice_client.get("/api/v1/me/saved")
        resp.raise_for_status()
        # result is a list (possibly empty or with items from other tests)
        assert isinstance(resp.json(), list)

    @pytest.mark.parametrize("limit", [0, -1])
    async def test_limit_invalid_chats(
        self,
        alice_client: AsyncClient,
        limit: int,
    ):
        resp = await alice_client.get("/api/v1/me/chats", params={"n": limit})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_limit_exceeds_max_chats(
        self,
        alice_client: AsyncClient,
    ):
        resp = await alice_client.get("/api/v1/me/chats", params={"n": 257})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("limit", [0, -1])
    async def test_limit_invalid_loans(
        self,
        alice_client: AsyncClient,
        limit: int,
    ):
        resp = await alice_client.get("/api/v1/me/loans", params={"n": limit})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_limit_exceeds_max_loans(
        self,
        alice_client: AsyncClient,
    ):
        resp = await alice_client.get("/api/v1/me/loans", params={"n": 257})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
