import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.schemas.user.private import UserPrivateRead
from tests.fixtures.items import ItemData


@pytest.mark.usefixtures("items")
class TestItemCreate:
    """Test item create endpoints."""

    def test_created_item_is_public(
        self,
        client: TestClient,
        alice: UserPrivateRead,
        alice_client: TestClient,
        alice_new_item_data: ItemData,
    ):
        """Check created item is then accessible in various lists."""

        # get current number of stars for alice
        resp = alice_client.get("/v1/me")
        resp.raise_for_status()
        old_stars_count = resp.json()["stars_count"]

        # create item
        resp = alice_client.post(
            "/v1/me/items",
            json=alice_new_item_data,
        )
        print(resp.text)
        resp.raise_for_status()
        added = resp.json()
        item_id = added["id"]

        # get item by id from global list
        resp = client.get(f"/v1/items/{item_id}")
        print(resp.text)
        resp.raise_for_status()
        read = resp.json()

        assert read["name"] == alice_new_item_data["name"]
        assert read["description"] == alice_new_item_data["description"]
        assert read["targeted_age_months"] == alice_new_item_data["targeted_age_months"]
        assert read["owner_id"] == alice.id
        assert read["images_names"] == alice_new_item_data["images"]
        assert {reg["id"] for reg in read["regions"]} == set(
            alice_new_item_data["regions"]
        )

        # get item in alice's list of items
        resp = client.get(f"/v1/users/{alice.id}/items/{item_id}")
        print(resp.text)
        resp.raise_for_status()
        read = resp.json()

        assert read["name"] == alice_new_item_data["name"]
        assert read["description"] == alice_new_item_data["description"]
        assert read["targeted_age_months"] == alice_new_item_data["targeted_age_months"]
        assert read["owner_id"] == alice.id
        assert read["images_names"] == alice_new_item_data["images"]
        assert {reg["id"] for reg in read["regions"]} == set(
            alice_new_item_data["regions"]
        )

        # get item by id from client list
        resp = alice_client.get(f"/v1/me/items/{item_id}")
        print(resp.text)
        resp.raise_for_status()
        read = resp.json()

        assert read["name"] == alice_new_item_data["name"]
        assert read["description"] == alice_new_item_data["description"]
        assert read["targeted_age_months"] == alice_new_item_data["targeted_age_months"]
        assert read["owner_id"] == alice.id
        assert read["images_names"] == alice_new_item_data["images"]
        assert {reg["id"] for reg in read["regions"]} == set(
            alice_new_item_data["regions"]
        )

        # check number of stars increment
        resp = alice_client.get("/v1/me")
        resp.raise_for_status()
        new_stars_count = resp.json()["stars_count"]
        assert new_stars_count == old_stars_count + 20


class TestItemCreateInvalid:
    """Test invalid item creation."""

    def test_item_no_region(
        self,
        alice_client: TestClient,
        alice_new_item_data: ItemData,
    ):
        """Check an item without region cannot be created."""

        # remove images
        alice_new_item_data = {
            **alice_new_item_data,
            "regions": [],
        }

        # create item
        resp = alice_client.post(
            "/v1/me/items",
            json=alice_new_item_data,
        )
        assert resp.is_error
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_item_no_image(
        self,
        alice_client: TestClient,
        alice_new_item_data: ItemData,
    ):
        """Check an item without image cannot be created."""

        # remove images
        alice_new_item_data = {
            **alice_new_item_data,
            "images": [],
        }

        # create item
        resp = alice_client.post(
            "/v1/me/items",
            json=alice_new_item_data,
        )
        assert resp.is_error
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_item_non_existing_image(
        self,
        alice_client: TestClient,
        alice_new_item_data: ItemData,
    ):
        # remove images
        alice_new_item_data = {
            **alice_new_item_data,
            "images": [*alice_new_item_data["images"], "xxxxxxxxxxxxxxxxxxxxx"],
        }

        # create item
        resp = alice_client.post(
            "/v1/me/items",
            json=alice_new_item_data,
        )

        assert resp.is_error
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_item_non_existing_region(
        self,
        alice_client: TestClient,
        alice_new_item_data: ItemData,
    ):
        # remove images
        alice_new_item_data = {
            **alice_new_item_data,
            "regions": [*alice_new_item_data["regions"], 99999],
        }

        # create item
        resp = alice_client.post(
            "/v1/me/items",
            json=alice_new_item_data,
        )

        assert resp.is_error
        assert resp.status_code == status.HTTP_404_NOT_FOUND
