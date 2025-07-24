from typing import Any

import pytest
from fastapi.testclient import TestClient
from unidecode import unidecode

from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import ItemQueryAvailability
from app.schemas.item.read import ItemRead
from app.schemas.user.private import UserPrivateRead
from app.utils.pagination import iter_chunks, iter_paginated_endpoint


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
        params: dict[str, Any] = {
            **({"n": count} if count is not None else {}),
        }

        assert len(many_items) >= 5, "poor data for testing"

        for items, expected_items in zip(
            iter_paginated_endpoint(
                client=client,
                url="/v1/items",
                params=params,
            ),
            iter_chunks(
                many_items[::-1],
                count=count or 32,
                append_empty=True,
            ),
            strict=True,
        ):
            print("page")
            assert [item["id"] for item in items] == [
                item.id for item in expected_items
            ]


@pytest.mark.usefixtures("many_items")
class TestItemsReadUserItems:
    """Test reading list of items owned by a user / the client."""

    def test_list_items_owned_by_alice(
        self,
        many_items: list[ItemPreviewRead],
        client: TestClient,
        alice: UserPrivateRead,
    ):
        """List items owned by Alice."""

        expected_item_ids = sorted(
            (item.id for item in many_items if item.owner_id == alice.id),
            reverse=True,
        )

        # get client items list
        item_ids = [
            item["id"]
            for page in iter_paginated_endpoint(
                url=f"/v1/users/{alice.id}/items",
                client=client,
            )
            for item in page
        ]

        assert item_ids == expected_item_ids

    def test_read_single_item_owned_by_alice(
        self,
        many_items: list[ItemPreviewRead],
        client: TestClient,
        alice: UserPrivateRead,
    ):
        """List items owned by Alice."""

        expected_item = next(
            iter([item for item in many_items if item.owner_id == alice.id])
        )

        resp = client.get(f"/v1/users/{alice.id}/items/{expected_item.id}")
        resp.raise_for_status()
        item = ItemRead.model_validate(resp.json())

        assert item == expected_item

    def test_list_items_owned_by_client(
        self,
        many_items: list[ItemPreviewRead],
        alice_client: TestClient,
        alice: UserPrivateRead,
    ):
        """List items owned by Alice."""

        expected_item_ids = sorted(
            (item.id for item in many_items if item.owner_id == alice.id),
            reverse=True,
        )

        # get client items list
        item_ids = [
            item["id"]
            for page in iter_paginated_endpoint(
                url="/v1/me/items",
                client=alice_client,
            )
            for item in page
        ]

        assert item_ids == expected_item_ids

    def test_read_single_item_owned_by_client(
        self,
        many_items: list[ItemPreviewRead],
        alice_client: TestClient,
        alice: UserPrivateRead,
    ):
        """List items owned by Alice."""

        expected_item = next(
            iter([item for item in many_items if item.owner_id == alice.id])
        )

        resp = alice_client.get(f"/v1/me/items/{expected_item.id}")
        resp.raise_for_status()
        item = ItemRead.model_validate(resp.json())

        assert item == expected_item


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

        expected_item_ids = sorted(
            (
                item.id
                for item in many_items
                if self.intersect(item.targeted_age_months.as_tuple, (lower, upper))
            ),
            reverse=True,
        )

        assert len(expected_item_ids) >= 5, "poor data for testing"

        # get client items list
        item_ids = [
            item["id"]
            for page in iter_paginated_endpoint(
                url="/v1/items",
                client=client,
                params={
                    "mo": self.format_range((lower, upper)),
                },
            )
            for item in page
        ]

        assert item_ids == expected_item_ids

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

        expected_item_ids = sorted(
            (
                item.id
                for item in many_items
                if self.check_availability(item, availability)
            ),
            reverse=True,
        )

        assert len(expected_item_ids) >= 5, "poor data for testing"

        # get client items list
        item_ids = [
            item["id"]
            for page in iter_paginated_endpoint(
                url="/v1/items",
                client=client,
                params={
                    "n": 256,
                    **{k: availability for k in ["av"] if availability is not None},
                },
            )
            for item in page
        ]

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

        expected_item_ids = sorted(
            (
                item.id
                for item in many_items
                if filter_regions is None
                or {reg.id for reg in item.regions}.intersection(filter_regions)
            ),
            reverse=True,
        )

        assert len(expected_item_ids) >= 5, "poor data for testing"

        # get client items list
        item_ids = [
            item["id"]
            for page in iter_paginated_endpoint(
                url="/v1/items",
                client=client,
                params={
                    "n": 256,
                    **{
                        k: filter_regions for k in ["reg"] if filter_regions is not None
                    },
                },
            )
            for item in page
        ]

        assert item_ids == expected_item_ids


# TODO include search words in the description of the item
@pytest.mark.usefixtures("some_items_with_french_names")
class TestItemsReadFilterWords:
    """Test item read with words filtering."""

    @pytest.mark.parametrize(
        "words", [["senat"], ["sénat"], ["Sénats"], ["senat", "xxxyyyzzz"]]
    )
    def test_list_item_with_french_word_senat(
        self,
        client: TestClient,
        words: list[str],
        some_items_with_french_names: list[ItemRead],
    ):
        """Filter item with words like 'senat'."""

        expected_item_ids = {
            item.id: item.name
            for item in some_items_with_french_names
            if "senat" in unidecode(item.name.lower())
        }

        # get client items list
        item_ids = {
            item["id"]: item["name"]
            for page in iter_paginated_endpoint(
                url="/v1/items",
                client=client,
                params={
                    "n": 256,
                    "q": words,
                },
            )
            for item in page
        }

        assert item_ids == expected_item_ids

    @pytest.mark.parametrize(
        "words", [["lecon"], ["leçon"], ["Leçon"], ["Lecon", "xxxyyyzzz"]]
    )
    def test_list_item_with_french_word_lecon(
        self,
        client: TestClient,
        words: list[str],
        some_items_with_french_names: list[ItemRead],
    ):
        """Filter item with words like 'lecon'."""

        expected_item_ids = {
            item.id: item.name
            for item in some_items_with_french_names
            if "lecon" in unidecode(item.name.lower())
        }

        # get client items list
        item_ids = {
            item["id"]: item["name"]
            for page in iter_paginated_endpoint(
                url="/v1/items",
                client=client,
                params={
                    "n": 256,
                    "q": words,
                },
            )
            for item in page
        }

        assert item_ids == expected_item_ids

    def test_list_item_with_french_word_bleu(
        self,
        client: TestClient,
        some_items_with_french_names: list[ItemRead],
    ):
        """Filter many item with words like 'bleu' to test pagination."""

        expected_item_ids = {
            item.id: item.name
            for item in some_items_with_french_names
            if "bleu" in unidecode(item.name.lower())
        }

        # get client items list
        item_ids = {
            item["id"]: item["name"]
            for page in iter_paginated_endpoint(
                url="/v1/items",
                client=client,
                params={
                    "n": 4,
                    "q": ["bleu"],
                },
            )
            for item in page
        }

        assert item_ids == expected_item_ids

    def test_order_of_list_item_with_french_word_senat_and_bleu(
        self,
        client: TestClient,
        some_items_with_french_names: list[ItemRead],
    ):
        """Check words matching order."""

        expected_item_names_order = [
            "Le sénat bleu",
            "Le senat bleus",
            "Les sénats bleus",
            "Le sénat du bien-être",
        ]

        # get client items list
        resp = client.get(
            url="/v1/items",
            params={
                "n": 4,
                "q": ["senat", "bleu"],
            },
        )
        resp.raise_for_status()
        item_names = [item["name"] for item in resp.json()]

        assert item_names == expected_item_names_order
