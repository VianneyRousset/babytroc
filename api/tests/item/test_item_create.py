import pytest
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

        # get item in alice's list of items
        resp = client.get(f"/v1/users/{alice.id}/items/{item_id}")
        print(resp.text)
        resp.raise_for_status()
        read = resp.json()

        assert read["name"] == alice_new_item_data["name"]
        assert read["description"] == alice_new_item_data["description"]
        assert read["targeted_age_months"] == alice_new_item_data["targeted_age_months"]
        assert read["owner_id"] == alice.id

        # get item by id from client list
        resp = alice_client.get(f"/v1/me/items/{item_id}")
        print(resp.text)
        resp.raise_for_status()
        read = resp.json()

        assert read["name"] == alice_new_item_data["name"]
        assert read["description"] == alice_new_item_data["description"]
        assert read["targeted_age_months"] == alice_new_item_data["targeted_age_months"]
        assert read["owner_id"] == alice.id
