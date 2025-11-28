import pytest
from httpx import AsyncClient

from tests.fixtures.items import ItemData


@pytest.mark.usefixtures("items")
class TestItemImages:
    """Test item iamges."""

    async def test_created_image_can_be_read(
        self,
        alice_client: AsyncClient,
        alice_items_image_data: str,
    ):
        """Upload image from client 0 and retrieve it from public await client."""

        # upload image
        resp = await alice_client.post(
            "https://babytroc.ch/api/v1/images",
            files={"file": alice_items_image_data},
        )
        resp.raise_for_status()
        name = resp.json()["name"]

        # request image
        resp = await alice_client.get(f"https://babytroc.ch/api/v1/images/{name}")
        resp.raise_for_status()

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
            "https://babytroc.ch/api/v1/me/items",
            json={
                **alice_new_item_data,
                "images": shuffled_names,
            },
        )
        resp.raise_for_status()
        item = resp.json()
        item_id = item["id"]

        # get item by id from global list
        resp = await alice_client.get(f"https://babytroc.ch/api/v1/items/{item_id}")
        print(resp.text)
        resp.raise_for_status()
        item = resp.json()

        # check the order of the images is preserved
        assert item["images"] == shuffled_names

    @staticmethod
    async def upload_image(client: AsyncClient, img: bytes) -> str:
        # upload image
        resp = await client.post(
            "https://babytroc.ch/api/v1/images",
            files={"file": img},
        )
        resp.raise_for_status()
        return resp.json()["name"]
