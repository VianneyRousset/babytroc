import pytest
from fastapi.testclient import TestClient

from tests.fixtures.items import ItemData


@pytest.mark.usefixtures("items")
class TestItemImages:
    """Test item iamges."""

    def test_created_image_can_be_read(
        self,
        alice_client: TestClient,
        alice_items_image_data: str,
    ):
        """Upload image from client 0 and retrieve it from public client."""

        # upload image
        resp = alice_client.post(
            "/v1/images",
            files={"file": alice_items_image_data},
        )
        resp.raise_for_status()
        name = resp.json()["name"]

        # request image
        resp = alice_client.get(f"/v1/images/{name}")
        resp.raise_for_status()

    def test_item_images_order(
        self,
        alice_client: TestClient,
        alice_items_image_data: bytes,
        alice_new_item_data: ItemData,
    ):
        """Check that item images order respects the created/updated one."""

        # upload 5 images
        names = [
            self.upload_image(alice_client, alice_items_image_data) for _ in range(5)
        ]

        shuffled_names = [names[i] for i in [3, 4, 1, 0, 2]]

        # create item with revsere custom order (different than upload order)
        resp = alice_client.post(
            "/v1/me/items",
            json={
                **alice_new_item_data,
                "images": shuffled_names,
            },
        )
        resp.raise_for_status()
        item = resp.json()
        item_id = item["id"]

        # get item by id from global list
        resp = alice_client.get(f"/v1/items/{item_id}")
        print(resp.text)
        resp.raise_for_status()
        item = resp.json()

        # check the order of the images is preserved
        assert item["images_names"] == shuffled_names

    @staticmethod
    def upload_image(client: TestClient, img: bytes) -> str:
        # upload image
        resp = client.post(
            "/v1/images",
            files={"file": img},
        )
        resp.raise_for_status()
        return resp.json()["name"]
