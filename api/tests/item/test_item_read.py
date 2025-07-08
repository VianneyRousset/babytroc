from itertools import zip_longest
from typing import Any
from urllib.parse import parse_qsl, urlparse

import pytest
from fastapi.testclient import TestClient

from app.schemas.item.read import ItemRead


@pytest.mark.usefixtures("many_items")
class TestItemsRead:
    """Test items read with no filtering."""

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


@pytest.mark.usefixtures("items")
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
            if self.intersect(item.targeted_age_months.as_tuple, (lower, upper))
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
