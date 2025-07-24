import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.schemas.item.read import ItemRead


@pytest.mark.usefixtures("items")
class TestItemDelete:
    """Test items delete endpoints."""

    def test_created_item_can_be_deleted(
        self,
        client: TestClient,
        alice_client: TestClient,
        alice_new_item: ItemRead,
        bob_client: TestClient,
    ):
        """Create an item and delete it."""

        # check item exists
        resp = client.get(f"/v1/items/{alice_new_item.id}")
        print(resp.text)
        resp.raise_for_status()

        # like and save item (check if the item can be deleted even if liked and saved)
        bob_client.post(f"/v1/me/liked/{alice_new_item.id}").raise_for_status()
        bob_client.post(f"/v1/me/saved/{alice_new_item.id}").raise_for_status()

        # delete item by id
        resp = alice_client.delete(f"/v1/me/items/{alice_new_item.id}")
        print(resp.text)
        resp.raise_for_status()

        # check item does not exists
        resp = client.get(f"/v1/items/{alice_new_item.id}")
        print(resp.text)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_created_item_cannot_be_deleted(
        self,
        client: TestClient,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_new_item: ItemRead,
    ):
        """Check that neither Bob nor an unlogged client can delete an unowned item."""

        # check item exists
        resp = client.get(f"/v1/items/{alice_new_item.id}")
        print(resp.text)
        resp.raise_for_status()

        # bob trying to delete item
        resp = bob_client.delete(f"/v1/me/items/{alice_new_item.id}")
        print(resp.text)

        # unlogged client trying to delete item
        resp = client.delete(f"/v1/me/items/{alice_new_item.id}")
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
