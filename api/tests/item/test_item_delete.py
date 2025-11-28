import pytest
from fastapi import status
from httpx import AsyncClient

from app.schemas.item.read import ItemRead


@pytest.mark.usefixtures("items")
class TestItemDelete:
    """Test items delete endpoints."""

    async def test_created_item_can_be_deleted(
        self,
        client: AsyncClient,
        alice_client: AsyncClient,
        alice_new_item: ItemRead,
        bob_client: AsyncClient,
    ):
        """Create an item and delete it."""

        # check item exists
        resp = await client.get(f"https://babytroc.ch/api/v1/items/{alice_new_item.id}")
        print(resp.text)
        resp.raise_for_status()

        # like and save item (check if the item can be deleted even if liked and saved)
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/me/liked/{alice_new_item.id}"
        )
        resp.raise_for_status()
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/me/saved/{alice_new_item.id}"
        )
        resp.raise_for_status()

        # delete item by id
        resp = await alice_client.delete(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}"
        )
        print(resp.text)
        resp.raise_for_status()

        # check item does not exists
        resp = await client.get(f"https://babytroc.ch/api/v1/items/{alice_new_item.id}")
        print(resp.text)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_created_item_cannot_be_deleted(
        self,
        client: AsyncClient,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        alice_new_item: ItemRead,
    ):
        """Check that neither Bob nor an unlogged client can delete an unowned item."""

        # check item exists
        resp = await client.get(f"https://babytroc.ch/api/v1/items/{alice_new_item.id}")
        print(resp.text)
        resp.raise_for_status()

        # bob trying to delete item
        resp = await bob_client.delete(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}"
        )
        print(resp.text)

        # unlogged client trying to delete item
        resp = await client.delete(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}"
        )
        print(resp.text)

        # get item by id from global list
        resp = await client.get(f"https://babytroc.ch/api/v1/items/{alice_new_item.id}")
        print(resp.text)
        resp.raise_for_status()
        item = ItemRead.model_validate(resp.json())

        # check data hasn't change
        assert item.name == alice_new_item.name
        assert item.description == alice_new_item.description
        assert item.targeted_age_months == alice_new_item.targeted_age_months
        assert item.owner.id == alice_new_item.owner.id
