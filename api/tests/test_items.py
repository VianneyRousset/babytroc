import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import inspect

from pprint import pprint
from .seed import apply_seed


@pytest.mark.usefixtures("_seed_db", scope="class")
class TestItems:
    @pytest.mark.run(order=1)
    @pytest.mark.asyncio(loop_scope="class")
    async def test_get_items(self, client: AsyncClient, db: AsyncSession):
        items = await client.get("/v1/items")

        pprint(items.json())
        assert items.json() == False

    @pytest.mark.run(order=2)
    @pytest.mark.asyncio(loop_scope="class")
    async def test_create_item(self):
        assert True
