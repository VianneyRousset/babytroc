import pytest
from httpx import AsyncClient


class TestItems:
    @pytest.mark.asyncio
    async def test_ping(self, client: AsyncClient, db_name: str):
        resp = await client.get("/")
        assert resp.status_code == 200
