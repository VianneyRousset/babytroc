import pytest
from redis.asyncio import Redis

from app.domains.item.services.cache import (
    invalidate_item_created,
    invalidate_item_deleted,
    invalidate_item_updated,
)
from app.infrastructure.cache_client import RedisCache


@pytest.fixture
async def redis_client(worker_id: str):
    db = 12
    client = Redis(host="localhost", port=6379, db=db)
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.fixture
def cache(redis_client):
    return RedisCache(redis_client)


class TestItemInvalidation:
    async def test_invalidate_item_created(self, cache):
        await cache.set("babytroc:items:list:abc123", "data", ttl=60)
        await cache.set("babytroc:user:1:items:def456", "data", ttl=60)
        await cache.set("babytroc:user:1", '{"stars": 0}', ttl=60)

        await invalidate_item_created(cache, owner_id=1)

        assert await cache.get("babytroc:items:list:abc123") is None
        assert await cache.get("babytroc:user:1:items:def456") is None
        assert await cache.get("babytroc:user:1") is None

    async def test_invalidate_item_updated(self, cache):
        await cache.set("babytroc:item:42", "data", ttl=60)
        await cache.set("babytroc:items:list:abc123", "data", ttl=60)
        await cache.set("babytroc:user:1:items:def456", "data", ttl=60)

        await invalidate_item_updated(cache, item_id=42, owner_id=1)

        assert await cache.get("babytroc:item:42") is None
        assert await cache.get("babytroc:items:list:abc123") is None
        assert await cache.get("babytroc:user:1:items:def456") is None

    async def test_invalidate_item_deleted(self, cache):
        await cache.set("babytroc:item:42", "data", ttl=60)
        await cache.set("babytroc:items:list:abc123", "data", ttl=60)
        await cache.set("babytroc:user:1:items:def456", "data", ttl=60)
        await cache.set("babytroc:user:1:loans:ghi789", "data", ttl=60)
        await cache.set("babytroc:user:1:chats", "data", ttl=60)

        await invalidate_item_deleted(cache, item_id=42, owner_id=1)

        assert await cache.get("babytroc:item:42") is None
        assert await cache.get("babytroc:items:list:abc123") is None
        assert await cache.get("babytroc:user:1:items:def456") is None
        assert await cache.get("babytroc:user:1:loans:ghi789") is None
        assert await cache.get("babytroc:user:1:chats") is None
