import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.schemas.image.read import ItemImageRead
from app.schemas.item.read import ItemRead


@pytest.mark.usefixtures("items")
class TestItemsUpdate:
    """Test items update endpoints."""

    def test_item_can_be_updated(
        self,
        client: TestClient,
        alice_client: TestClient,
        alice_new_item: ItemRead,
        alice_items_image: ItemImageRead,
    ):
        """Check that an item can be updated."""

        # update item name
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}",
            json={
                "name": "forest",
                "targeted_age_months": "10-14",
                "images": [*alice_new_item.images_names, alice_items_image.name],
                "regions": [1, 2],
            },
        )
        print(resp.text)
        resp.raise_for_status()

        # get item by id from global list
        resp = client.get(f"/v1/items/{alice_new_item.id}")
        print(resp.text)
        resp.raise_for_status()
        read = resp.json()

        assert read["name"] == "forest"
        assert read["description"] == alice_new_item.description
        assert read["targeted_age_months"] == "10-14"
        assert read["owner_id"] == alice_new_item.owner_id
        assert read["images_names"] == [
            *alice_new_item.images_names,
            alice_items_image.name,
        ]
        assert {reg["id"] for reg in read["regions"]} == {1, 2}


class TestItemUpdateInvalid:
    """Test invalid item update."""

    def test_no_credentials(
        self,
        client: TestClient,
        bob_client: TestClient,
        alice_new_item: ItemRead,
    ):
        """Check that neither Bob nor an unlogged client can update Alice's item."""

        # bob trying to update item name
        resp = bob_client.post(
            f"/v1/me/items/{alice_new_item.id}",
            json={"name": "forest"},
        )
        print(resp.text)

        # unlogged client trying to update item name
        resp = client.post(
            f"/v1/me/items/{alice_new_item.id}",
            json={"name": "forest"},
        )
        print(resp.text)

        # get item by id from global list
        resp = client.get(f"/v1/items/{alice_new_item.id}")
        print(resp.text)
        resp.raise_for_status()
        read = resp.json()

        # check data hasn't change
        assert read["name"] == alice_new_item.name
        assert read["description"] == alice_new_item.description
        assert (
            read["targeted_age_months"]
            == alice_new_item.targeted_age_months.model_dump()
        )
        assert read["owner_id"] == alice_new_item.owner_id

    def test_non_existing_item(
        self,
        alice_client: TestClient,
    ):
        """Check that updating an non-existing item returns 404."""

        resp = alice_client.post(
            "/v1/me/items/9999",
            json={"name": "New item name"},
        )
        print(resp.text)
        assert resp.is_error
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_no_region(
        self,
        alice_client: TestClient,
        alice_new_item: ItemRead,
    ):
        """Check an item without region cannot be created."""

        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}",
            json={"regions": []},
        )
        print(resp.text)
        assert resp.is_error
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_no_image(
        self,
        alice_client: TestClient,
        alice_new_item: ItemRead,
    ):
        """Check an item without image cannot be created."""

        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}",
            json={"images": []},
        )
        print(resp.text)
        assert resp.is_error
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_non_existing_image(
        self,
        alice_client: TestClient,
        alice_new_item: ItemRead,
    ):
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}",
            json={
                "images": [*alice_new_item.images_names, "xxxxxxxxxxxxxxxxxxxx"],
            },
        )
        print(resp.text)
        assert resp.is_error
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_non_existing_region(
        self,
        alice_client: TestClient,
        alice_new_item: ItemRead,
    ):
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}",
            json={
                "regions": [*[reg.id for reg in alice_new_item.regions], 9999],
            },
        )
        print(resp.text)
        assert resp.is_error
        assert resp.status_code == status.HTTP_404_NOT_FOUND
