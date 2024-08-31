import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item as ItemDB


async def get_db_items(db: AsyncSession) -> list:
    return [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "creation_date": item.creation_date.isoformat(),
        }
        for item in await db.scalars(select(ItemDB))
    ]


class TestReadItems:
    @pytest.mark.usefixtures("_seed_db")
    @pytest.mark.asyncio
    async def test_list_items(self, client: AsyncClient, db: AsyncSession):
        resp = await client.get("/v1/items")

        assert resp.status_code == 200, "GET request did not succeed"

        api_items = resp.json()
        db_items = await get_db_items(db)

        assert len(api_items) == len(
            db_items
        ), "Number of items in API response doesn't match database"

        assert type(api_items) is list, "API response is not a list"

        db_items = {item["id"]: item for item in db_items}
        api_items = {item["id"]: item for item in api_items}

        # compare items
        assert (
            db_items == api_items
        ), "Mismatch in items between database and API response"


class TestReadSingleItem:
    @pytest.mark.usefixtures("_seed_db")
    @pytest.mark.asyncio
    async def test_read_single_item(self, client: AsyncClient, db: AsyncSession):
        db_items = {item["id"]: item for item in await get_db_items(db)}

        for item_id, db_item in db_items.items():
            # get first item
            resp = await client.get(f"/v1/items/{item_id}")

            assert (
                resp.status_code == 200
            ), f"GET request did not succeed for item_id {item_id}"

            api_item = resp.json()

            assert api_item == db_item
