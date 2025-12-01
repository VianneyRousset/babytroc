import pytest
from httpx import AsyncClient

from app.schemas.item.read import ItemRead


@pytest.mark.usefixtures("many_items")
class TestItemLike:
    """Test item likes."""

    async def test_read_pages(
        self,
        bob_client: AsyncClient,
        alice_items: list[ItemRead],
    ):
        item = alice_items[-1]

        # like alice items
        resp = await bob_client.post(
            url=f"https://babytroc.ch/api/v1/me/liked/{item.id}"
        )
        resp.raise_for_status()

        # check flagged as liked in item read
        resp = await bob_client.get(f"https://babytroc.ch/api/v1/items/{item.id}")
        resp.raise_for_status()

        print(">>", resp.json())

        assert resp.json()["liked"], "ItemRead should mark item as liked"

        # check appears in the list of liked items
        resp = await bob_client.get("https://babytroc.ch/api/v1/me/liked")
        resp.raise_for_status()
        assert [item["id"] for item in resp.json()] == [item.id]
