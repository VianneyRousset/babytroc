import pytest
from httpx import AsyncClient

from app.schemas.item.read import ItemRead
from tests.fixtures.items import ItemData


@pytest.mark.usefixtures("items")
class TestItemImages:
    """Test item images."""

    async def test_upload_image_returns_name(
        self,
        alice_client: AsyncClient,
        alice_items_image_data: bytes,
    ):
        """Upload image and verify response contains a name."""

        resp = await alice_client.post(
            "/api/v1/images",
            files={"file": alice_items_image_data},
        )
        resp.raise_for_status()
        data = resp.json()
        assert "name" in data
        assert len(data["name"]) == 32  # uuid hex

    async def test_item_images_order(
        self,
        alice_client: AsyncClient,
        alice_items_image_data: bytes,
        alice_new_item_data: ItemData,
    ):
        """Check that item images order respects the created/updated one."""

        # upload 5 images
        names: list[str] = [
            await self.upload_image(alice_client, alice_items_image_data)
            for _ in range(5)
        ]

        shuffled_names = [names[i] for i in [3, 4, 1, 0, 2]]

        # create item with custom order (different than upload order)
        resp = await alice_client.post(
            "/api/v1/me/items",
            json={
                **alice_new_item_data,
                "images": shuffled_names,
            },
        )
        resp.raise_for_status()
        item = resp.json()
        item_id = item["id"]

        # get item by id from global list
        resp = await alice_client.get(f"/api/v1/items/{item_id}")
        resp.raise_for_status()
        item = ItemRead.model_validate(resp.json())

        # check the order of the images is preserved
        assert item.image_names == shuffled_names

    @staticmethod
    async def upload_image(client: AsyncClient, img: bytes) -> str:
        resp = await client.post(
            "/api/v1/images",
            files={"file": img},
        )
        resp.raise_for_status()
        return resp.json()["name"]
