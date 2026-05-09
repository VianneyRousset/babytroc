from typing import Any

from httpx import AsyncClient

from app.domains.category.schemas.read import CategoryRead
from app.domains.item.schemas.read import ItemRead
from app.shared.pagination_utils import iter_paginated_endpoint


class TestCategoriesList:
    """Test GET /api/v1/utils/categories."""

    async def test_list_categories(
        self,
        alice_client: AsyncClient,
        categories: list[CategoryRead],
    ):
        """Returns all categories."""
        resp = await alice_client.get("/api/v1/utils/categories")
        resp.raise_for_status()

        data = resp.json()
        slugs = {cat["slug"] for cat in data}

        assert len(data) == len(categories)
        for cat in categories:
            assert cat.slug in slugs

    async def test_list_categories_has_parents_and_children(
        self,
        alice_client: AsyncClient,
        categories: list[CategoryRead],
    ):
        """Response contains both parent and child categories."""
        resp = await alice_client.get("/api/v1/utils/categories")
        resp.raise_for_status()

        data = resp.json()
        parents = [c for c in data if c["parent_slug"] is None]
        children = [c for c in data if c["parent_slug"] is not None]

        assert len(parents) >= 1
        assert len(children) >= 1


class TestItemCategoryFilter:
    """Test /api/v1/items?cat=... filtering."""

    async def test_filter_by_child_category(
        self,
        alice_client: AsyncClient,
        alice_items_with_categories: list[ItemRead],
        categories: list[CategoryRead],
    ):
        """Filtering by a child category returns only items tagged with that child."""
        child_slug = "clothing-bodysuits"

        expected_ids = {
            item.id
            for item in alice_items_with_categories
            if child_slug in item.category_slugs
        }
        assert len(expected_ids) >= 1, "poor test data"

        params: dict[str, Any] = {"cat": [child_slug], "av": "a", "n": 256}
        all_ids: set[int] = set()

        async for items in iter_paginated_endpoint(
            url="/api/v1/items",
            client=alice_client,
            params=params,
        ):
            all_ids |= {item["id"] for item in items}

        assert expected_ids <= all_ids

    async def test_filter_by_parent_includes_children(
        self,
        alice_client: AsyncClient,
        alice_items_with_categories: list[ItemRead],
        categories: list[CategoryRead],
    ):
        """Filtering by parent category returns items in parent + all children."""
        parent_slug = "clothing"
        family_slugs = {parent_slug} | {
            cat.slug for cat in categories if cat.parent_slug == parent_slug
        }

        expected_ids = {
            item.id
            for item in alice_items_with_categories
            if family_slugs & set(item.category_slugs)
        }
        assert len(expected_ids) >= 2, "poor test data"

        params: dict[str, Any] = {"cat": [parent_slug], "av": "a", "n": 256}
        all_ids: set[int] = set()

        async for items in iter_paginated_endpoint(
            url="/api/v1/items",
            client=alice_client,
            params=params,
        ):
            all_ids |= {item["id"] for item in items}

        assert expected_ids <= all_ids

    async def test_filter_by_multiple_categories(
        self,
        alice_client: AsyncClient,
        alice_items_with_categories: list[ItemRead],
        categories: list[CategoryRead],
    ):
        """Filtering by multiple categories returns union."""
        slugs = ["clothing-bodysuits", "toys-bath"]

        expected_ids = {
            item.id
            for item in alice_items_with_categories
            if set(slugs) & set(item.category_slugs)
        }
        assert len(expected_ids) >= 1, "poor test data"

        params: dict[str, Any] = {"cat": slugs, "av": "a", "n": 256}
        all_ids: set[int] = set()

        async for items in iter_paginated_endpoint(
            url="/api/v1/items",
            client=alice_client,
            params=params,
        ):
            all_ids |= {item["id"] for item in items}

        assert expected_ids <= all_ids

    async def test_no_filter_returns_all(
        self,
        alice_client: AsyncClient,
        alice_items_with_categories: list[ItemRead],
    ):
        """No category filter returns all items."""
        params: dict[str, Any] = {"av": "a", "n": 256}
        all_ids: set[int] = set()

        async for items in iter_paginated_endpoint(
            url="/api/v1/items",
            client=alice_client,
            params=params,
        ):
            all_ids |= {item["id"] for item in items}

        expected_ids = {item.id for item in alice_items_with_categories}
        assert expected_ids <= all_ids
