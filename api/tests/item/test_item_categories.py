from httpx import AsyncClient

from app.schemas.category.read import CategoryRead


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
