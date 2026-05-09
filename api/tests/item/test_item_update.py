import pytest
from fastapi import status
from httpx import AsyncClient

from babytroc.domains.image.schemas.read import ItemImageRead
from babytroc.domains.item.schemas.base import MonthRange
from babytroc.domains.item.schemas.read import ItemRead


@pytest.mark.usefixtures("items")
class TestItemsUpdate:
    """Test items update endpoints."""

    async def test_item_can_be_updated(
        self,
        client: AsyncClient,
        alice_client: AsyncClient,
        alice_new_item: ItemRead,
        alice_items_image: ItemImageRead,
    ):
        """Check that an item can be updated."""

        # update item name
        resp = await alice_client.post(
            f"/api/v1/me/items/{alice_new_item.id}",
            json={
                "name": "forest",
                "targeted_age_months": "10-14",
                "images": [*alice_new_item.image_names, alice_items_image.name],
                "regions": [1, 2],
            },
        )
        resp.raise_for_status()

        # get item by id from global list
        resp = await client.get(f"/api/v1/items/{alice_new_item.id}")
        resp.raise_for_status()
        item = ItemRead.model_validate(resp.json())

        assert item.name == "forest"
        assert item.description == alice_new_item.description
        assert item.targeted_age_months == MonthRange("10-14")
        assert item.owner.id == alice_new_item.owner.id
        assert item.image_names == [
            *alice_new_item.image_names,
            alice_items_image.name,
        ]
        assert item.region_ids == {1, 2}


class TestItemUpdateInvalid:
    """Test invalid item update."""

    async def test_no_credentials(
        self,
        client: AsyncClient,
        bob_client: AsyncClient,
        alice_new_item: ItemRead,
    ):
        """Check that neither Bob nor an unlogged client can update Alice's item."""

        # bob trying to update item name
        resp = await bob_client.post(
            f"/api/v1/me/items/{alice_new_item.id}",
            json={"name": "forest"},
        )

        # unlogged client trying to update item name
        resp = await client.post(
            f"/api/v1/me/items/{alice_new_item.id}",
            json={"name": "forest"},
        )

        # get item by id from global list
        resp = await client.get(f"/api/v1/items/{alice_new_item.id}")
        resp.raise_for_status()
        read = resp.json()

        # check data hasn't change
        assert read["name"] == alice_new_item.name
        assert read["description"] == alice_new_item.description
        assert (
            read["targeted_age_months"]
            == alice_new_item.targeted_age_months.model_dump()
        )
        assert read["owner"]["id"] == alice_new_item.owner.id

    async def test_non_existing_item(
        self,
        alice_client: AsyncClient,
    ):
        """Check that updating an non-existing item returns 404."""

        resp = await alice_client.post(
            "/api/v1/me/items/9999",
            json={"name": "New item name"},
        )
        assert resp.is_error
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_no_region(
        self,
        alice_client: AsyncClient,
        alice_new_item: ItemRead,
    ):
        """Check an item without region cannot be created."""

        resp = await alice_client.post(
            f"/api/v1/me/items/{alice_new_item.id}",
            json={"regions": []},
        )
        assert resp.is_error
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_no_image(
        self,
        alice_client: AsyncClient,
        alice_new_item: ItemRead,
    ):
        """Check an item without image cannot be created."""

        resp = await alice_client.post(
            f"/api/v1/me/items/{alice_new_item.id}",
            json={"images": []},
        )
        assert resp.is_error
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_non_existing_image(
        self,
        alice_client: AsyncClient,
        alice_new_item: ItemRead,
    ):
        resp = await alice_client.post(
            f"/api/v1/me/items/{alice_new_item.id}",
            json={
                "images": [*alice_new_item.image_names, "xxxxxxxxxxxxxxxxxxxx"],
            },
        )
        assert resp.is_error
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_non_existing_region(
        self,
        alice_client: AsyncClient,
        alice_new_item: ItemRead,
    ):
        resp = await alice_client.post(
            f"/api/v1/me/items/{alice_new_item.id}",
            json={
                "regions": [*alice_new_item.region_ids, 9999],
            },
        )
        assert resp.is_error
        assert resp.status_code == status.HTTP_404_NOT_FOUND
