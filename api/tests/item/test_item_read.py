from itertools import zip_longest
from typing import Any
from urllib.parse import parse_qsl, urlparse

import pytest
from fastapi.testclient import TestClient

from app.schemas.item.query import ItemQueryAvailability
from app.schemas.item.read import ItemRead


@pytest.mark.usefixtures("many_items")
class TestItemsRead:
    """Test items read with no filtering."""

    @pytest.mark.parametrize("count", [None, 16, 7])
    def test_read_pages(
        self,
        client: TestClient,
        many_items: list[ItemRead],
        count: int | None,
    ):
        cursor: dict[str, Any] = {}

        for i, expected_items in enumerate(self.grouper(many_items[::-1], count or 32)):
            print(f"page #{i} cursor:", cursor)

            params = cursor

            if count is not None:
                params = {
                    **params,
                    "n": count,
                }

            # get next page
            resp = client.get(
                url="/v1/items",
                params=params,
            )
            print(resp.json())
            resp.raise_for_status()
            cursor = dict(parse_qsl(urlparse(resp.links["next"]["url"]).query))

            assert [item["id"] for item in resp.json()] == [
                item.id for item in expected_items
            ]

    @staticmethod
    def grouper(iterable, count):
        "grouper('abcdefgh', 3) --> ('a','b','c'), ('d','e','f'), ('g','h')"
        groups = zip_longest(*[iter(iterable)] * count)
        return [filter(lambda v: v is not None, group) for group in groups]


@pytest.mark.usefixtures("many_items")
class TestItemsReadFilterTargetedAgeMonth:
    """Test item read with targeted_age_month filtering."""

    @pytest.mark.parametrize("lower", [None, 0, 5, 10, 15, 20])
    @pytest.mark.parametrize("upper", [None, 0, 5, 10, 15, 20])
    def test_list_item_filter_targeted_age_month(
        self,
        client: TestClient,
        many_items: list[ItemRead],
        lower: int | None,
        upper: int | None,
    ):
        """Filter items list by targeted age months (mo)."""

        lower = None
        upper = 5

        expected_items = {
            item.id
            for item in many_items
            if item.available
            if self.intersect(item.targeted_age_months.as_tuple, (lower, upper))
        }

        assert len(expected_items) >= 5, "poor data for testing"

        # get client items list
        resp = client.get(
            url="/v1/items",
            params={
                "mo": self.format_range((lower, upper)),
                "n": 2 * len(expected_items),
                "av": "y",
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

        return res


@pytest.mark.usefixtures("many_items")
class TestItemsReadFilterAvailability:
    """Test item read with availability filtering."""

    @pytest.mark.parametrize("availability", [None, "a", "y", "n"])
    def test_list_item_filter_availability(
        self,
        client: TestClient,
        many_items: list[ItemRead],
        availability: ItemQueryAvailability | None,
    ):
        """Filter items list by availability (av)."""

        expected_item_ids = {
            item.id
            for item in many_items
            if self.check_availability(item, availability)
        }

        assert len(expected_item_ids) >= 5, "poor data for testing"

        # get client items list
        item_ids = self.accumulate_all_item_ids_pages(
            url="/v1/items",
            client=client,
            params={
                "n": 256,
                **{k: availability for k in ["av"] if availability is not None},
            },
        )

        assert item_ids == expected_item_ids

    @staticmethod
    def check_availability(
        item: ItemRead,
        availability: ItemQueryAvailability | None,
    ) -> bool:
        """Return True if `item` respects `availability`."""

        # default availability
        availability = (
            ItemQueryAvailability.all if availability is None else availability
        )

        if availability == ItemQueryAvailability.all:
            return True

        if availability == ItemQueryAvailability.yes:
            return item.available

        return not item.available

    @staticmethod
    def accumulate_all_item_ids_pages(
        url: str,
        client: TestClient,
        params=None,
    ) -> set[int]:
        params = params or {}

        items = set[int]()

        maxn = 100

        for _ in range(maxn):
            # get next page
            resp = client.get(
                url=url,
                params=params,
            )
            resp.raise_for_status()
            params = dict(parse_qsl(urlparse(resp.links["next"]["url"]).query))

            new_items = resp.json()

            if len(new_items) == 0:
                return items

            items = items.union(item["id"] for item in new_items)

        msg = "Max iteration reached"
        raise RuntimeError(msg)


@pytest.mark.usefixtures("many_items")
class TestItemsReadFilterRegions:
    """Test item read with availability filtering."""

    @pytest.mark.parametrize("filter_regions", [None, [1], [2], [1, 2]])
    def test_list_item_filter_regions(
        self,
        client: TestClient,
        many_items: list[ItemRead],
        filter_regions: set[int] | None,
    ):
        """Filter items list by availability (av)."""

        expected_item_ids = {
            item.id
            for item in many_items
            if filter_regions is None
            or {reg.id for reg in item.regions}.intersection(filter_regions)
        }

        assert len(expected_item_ids) >= 5, "poor data for testing"

        # get client items list
        item_ids = self.accumulate_all_item_ids_pages(
            url="/v1/items",
            client=client,
            params={
                "n": 256,
                **{k: filter_regions for k in ["reg"] if filter_regions is not None},
            },
        )

        assert item_ids == expected_item_ids

    @staticmethod
    def accumulate_all_item_ids_pages(
        url: str,
        client: TestClient,
        params=None,
    ) -> set[int]:
        params = params or {}

        items = set[int]()

        maxn = 100

        for _ in range(maxn):
            # get next page
            resp = client.get(
                url=url,
                params=params,
            )
            resp.raise_for_status()
            params = dict(parse_qsl(urlparse(resp.links["next"]["url"]).query))

            new_items = resp.json()

            if len(new_items) == 0:
                return items

            items = items.union(item["id"] for item in new_items)

        msg = "Max iteration reached"
        raise RuntimeError(msg)
