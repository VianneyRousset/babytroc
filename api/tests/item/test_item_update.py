import pytest
from fastapi.testclient import TestClient

from app.schemas.item.read import ItemRead


@pytest.mark.usefixtures("items")
class TestItemsUpdate:
    """Test items update endpoints."""

    def test_item_can_be_updated(
        self,
        client: TestClient,
        alice_client: TestClient,
        alice_new_item: ItemRead,
    ):
        """Check that an item can be updated."""

        # update item name
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}",
            json={"name": "forest"},
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
        assert (
            read["targeted_age_months"]
            == alice_new_item.targeted_age_months.model_dump()
        )
        assert read["owner_id"] == alice_new_item.owner_id

    def test_item_cannot_be_updated(
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
