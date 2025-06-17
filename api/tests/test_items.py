from itertools import zip_longest
from typing import Any
from urllib.parse import parse_qsl, urlparse

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.schemas.item.read import ItemRead
from app.schemas.user.private import UserPrivateRead
from tests.fixtures.items import ItemData


@pytest.mark.usefixtures("items")
class TestItemsCreateUpdateDelete:
    """Test items create, update and delete endpoints."""

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
        assert (
            tuple(read["targeted_age_months"])
            == alice_new_item_data["targeted_age_months"]
        )
        assert read["owner_id"] == alice.id

        # get item in alice's list of items
        resp = client.get(f"/v1/users/{alice.id}/items/{item_id}")
        print(resp.text)
        resp.raise_for_status()
        read = resp.json()

        assert read["name"] == alice_new_item_data["name"]
        assert read["description"] == alice_new_item_data["description"]
        assert (
            tuple(read["targeted_age_months"])
            == alice_new_item_data["targeted_age_months"]
        )
        assert read["owner_id"] == alice.id

        # get item by id from client list
        resp = alice_client.get(f"/v1/me/items/{item_id}")
        print(resp.text)
        resp.raise_for_status()
        read = resp.json()

        assert read["name"] == alice_new_item_data["name"]
        assert read["description"] == alice_new_item_data["description"]
        assert (
            tuple(read["targeted_age_months"])
            == alice_new_item_data["targeted_age_months"]
        )
        assert read["owner_id"] == alice.id

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
        assert tuple(read["targeted_age_months"]) == alice_new_item.targeted_age_months
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
        assert tuple(read["targeted_age_months"]) == alice_new_item.targeted_age_months
        assert read["owner_id"] == alice_new_item.owner_id

    def test_created_item_can_be_deleted(
        self,
        client: TestClient,
        alice_client: TestClient,
        alice_new_item: ItemRead,
    ):
        """Create an item and delete it."""

        # check item exists
        resp = client.get(f"/v1/items/{alice_new_item.id}")
        print(resp.text)
        resp.raise_for_status()

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
        assert tuple(read["targeted_age_months"]) == alice_new_item.targeted_age_months
        assert read["owner_id"] == alice_new_item.owner_id


class TestItemsFiltering:
    """Test items read filtering endpoints."""

    @pytest.mark.parametrize("lower", [None, 0, 5, 10, 15, 20])
    @pytest.mark.parametrize("upper", [None, 0, 5, 10, 15, 20])
    def test_list_item_filter_targeted_age_month(
        self,
        client: TestClient,
        items: list[ItemRead],
        lower: int | None,
        upper: int | None,
    ):
        """Filter items list by targeted age months (mo)."""

        lower = None
        upper = 5

        expected_items = {
            item.id
            for item in items
            if self.intersect(item.targeted_age_months, (lower, upper))
        }

        # get client items list
        resp = client.get(
            url="/v1/items",
            params={
                "mo": self.format_range((lower, upper)),
            },
        )
        resp.raise_for_status()

        assert {item["id"] for item in resp.json()} == expected_items

    @staticmethod
    def format_range(r: tuple[int | None, int | None]) -> str:
        """Format range into string."""

        lower, upper = r

        lower_str = "" if lower is None else f"{lower:d}"
        upper_str = "" if upper is None else f"{upper:d}"

        return f"{lower_str}-{upper_str}"

    @staticmethod
    def intersect(
        a: tuple[int | None, int | None],
        b: tuple[int | None, int | None],
    ) -> bool:
        """Returns True if range a and b intersect."""

        a_lower, a_upper = a
        b_lower, b_upper = b

        a_lower = -1000 if a_lower is None else a_lower
        b_lower = -1000 if b_lower is None else b_lower

        a_upper = 1000 if a_upper is None else a_upper
        b_upper = 1000 if b_upper is None else b_upper

        res = a_lower <= b_upper and a_upper >= b_lower

        print(a, b, "->", res)
        return res


@pytest.mark.usefixtures("many_items")
class TestItemsPagination:
    """Test items read pagination."""

    @pytest.mark.parametrize("count", [16, 7])
    def test_read_pages(
        self,
        client: TestClient,
        many_items: list[ItemRead],
        count: int | None,
    ):
        cursor: dict[str, Any] = {}

        for i, expected_items in enumerate(self.grouper(many_items[::-1], count)):
            print(f"page #{i} cursor:", cursor)

            # get next page
            resp = client.get(
                url="/v1/items",
                params={
                    "n": count,
                    **cursor,
                },
            )
            resp.raise_for_status()
            cursor = dict(parse_qsl(urlparse(resp.links["next"]["url"]).query))

            assert [item["id"] for item in resp.json()] == [
                item.id for item in expected_items
            ]

    @staticmethod
    def grouper(iterable, count):
        "grouper(3, 'abcdefgh') --> ('a','b','c'), ('d','e','f'), ('g','h')"
        groups = zip_longest(*[iter(iterable)] * count)
        return [filter(lambda v: v is not None, group) for group in groups]
