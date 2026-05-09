from __future__ import annotations

from typing import TYPE_CHECKING

from app.infrastructure.cache_keys import key_categories, key_regions, key_user

if TYPE_CHECKING:
    from fastapi import FastAPI
    from httpx import AsyncClient

    from app.infrastructure.cache_client import Cache
    from app.domains.user.schemas.private import UserPrivateRead


class TestCacheIntegrationRegions:
    """Test that regions are cached and returned from cache on second call."""

    async def test_regions_cached(
        self,
        alice_client: AsyncClient,
        app: FastAPI,
        regions,
    ):
        cache: Cache = app.state.cache

        r1 = await alice_client.get("/api/v1/utils/regions")
        assert r1.status_code == 200

        cached = await cache.get(key_regions())
        assert cached is not None

        r2 = await alice_client.get("/api/v1/utils/regions")
        assert r2.status_code == 200
        assert r2.json() == r1.json()


class TestCacheIntegrationCategories:
    """Test that categories are cached and returned from cache on second call."""

    async def test_categories_cached(
        self,
        alice_client: AsyncClient,
        app: FastAPI,
        categories,
    ):
        cache: Cache = app.state.cache

        r1 = await alice_client.get("/api/v1/utils/categories")
        assert r1.status_code == 200

        cached = await cache.get(key_categories())
        assert cached is not None

        r2 = await alice_client.get("/api/v1/utils/categories")
        assert r2.status_code == 200
        assert r2.json() == r1.json()


class TestCacheIntegrationUsers:
    """Test that user profiles are cached on read."""

    async def test_user_profile_cached(
        self,
        alice_client: AsyncClient,
        app: FastAPI,
        alice: UserPrivateRead,
    ):
        cache: Cache = app.state.cache
        user_id = alice.id

        r1 = await alice_client.get(f"/api/v1/users/{user_id}")
        assert r1.status_code == 200

        cached = await cache.get(key_user(user_id))
        assert cached is not None

        r2 = await alice_client.get(f"/api/v1/users/{user_id}")
        assert r2.status_code == 200
        assert r2.json() == r1.json()

    async def test_user_profile_cache_contains_correct_data(
        self,
        alice_client: AsyncClient,
        app: FastAPI,
        alice: UserPrivateRead,
    ):
        cache: Cache = app.state.cache
        user_id = alice.id

        r = await alice_client.get(f"/api/v1/users/{user_id}")
        assert r.status_code == 200
        data = r.json()

        assert data["id"] == user_id
        assert data["name"] == alice.name

        cached = await cache.get(key_user(user_id))
        assert cached is not None


class TestCacheIntegrationItemsInvalidation:
    """Test item cache invalidation via cache pattern operations."""

    async def test_items_list_pattern_invalidation(
        self,
        app: FastAPI,
    ):
        cache: Cache = app.state.cache

        await cache.set("babytroc:items:list:abc123", '["fake1"]', ttl=60)
        await cache.set("babytroc:items:list:def456", '["fake2"]', ttl=60)
        await cache.set("babytroc:user:1", '{"id": 1}', ttl=60)

        assert await cache.get("babytroc:items:list:abc123") is not None
        assert await cache.get("babytroc:items:list:def456") is not None

        await cache.delete_pattern("babytroc:items:list:*")

        assert await cache.get("babytroc:items:list:abc123") is None
        assert await cache.get("babytroc:items:list:def456") is None
        # Unrelated key not affected
        assert await cache.get("babytroc:user:1") is not None

    async def test_user_cache_invalidation_via_pattern(
        self,
        app: FastAPI,
        alice: UserPrivateRead,
    ):
        cache: Cache = app.state.cache
        user_id = alice.id

        await cache.set(f"babytroc:user:{user_id}:items:abc", "data", ttl=60)
        await cache.set(f"babytroc:user:{user_id}:loans:xyz", "data", ttl=60)
        await cache.set(f"babytroc:user:{user_id}", '{"id": 1}', ttl=60)

        await cache.delete_pattern(f"babytroc:user:{user_id}:*")
        await cache.delete(f"babytroc:user:{user_id}")

        assert await cache.get(f"babytroc:user:{user_id}:items:abc") is None
        assert await cache.get(f"babytroc:user:{user_id}:loans:xyz") is None
        assert await cache.get(f"babytroc:user:{user_id}") is None
