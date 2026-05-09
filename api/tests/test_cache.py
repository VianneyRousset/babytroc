import pytest
from redis.asyncio import Redis

from app.infrastructure.cache_client import RedisCache


@pytest.fixture
async def redis_client(worker_id: str):
    db = 11
    client = Redis(host="localhost", port=6379, db=db)
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.fixture
def cache(redis_client):
    return RedisCache(redis_client)


class TestCache:
    async def test_get_miss(self, cache):
        result = await cache.get("babytroc:test:miss")
        assert result is None

    async def test_set_and_get(self, cache):
        await cache.set("babytroc:test:key", '{"a": 1}', ttl=60)
        result = await cache.get("babytroc:test:key")
        assert result == b'{"a": 1}'

    async def test_delete(self, cache):
        await cache.set("babytroc:test:del", "value", ttl=60)
        await cache.delete("babytroc:test:del")
        result = await cache.get("babytroc:test:del")
        assert result is None

    async def test_delete_multiple(self, cache):
        await cache.set("babytroc:test:a", "1", ttl=60)
        await cache.set("babytroc:test:b", "2", ttl=60)
        await cache.delete("babytroc:test:a", "babytroc:test:b")
        assert await cache.get("babytroc:test:a") is None
        assert await cache.get("babytroc:test:b") is None

    async def test_delete_pattern(self, cache):
        await cache.set("babytroc:test:pattern:1", "a", ttl=60)
        await cache.set("babytroc:test:pattern:2", "b", ttl=60)
        await cache.set("babytroc:test:other", "c", ttl=60)
        await cache.delete_pattern("babytroc:test:pattern:*")
        assert await cache.get("babytroc:test:pattern:1") is None
        assert await cache.get("babytroc:test:pattern:2") is None
        assert await cache.get("babytroc:test:other") == b"c"

    async def test_get_or_set_miss(self, cache):
        async def factory():
            return '{"computed": true}'

        result = await cache.get_or_set(
            "babytroc:test:factory", ttl=60, factory=factory
        )
        assert result == '{"computed": true}'
        assert await cache.get("babytroc:test:factory") == b'{"computed": true}'

    async def test_get_or_set_hit(self, cache):
        await cache.set("babytroc:test:cached", '{"cached": true}', ttl=60)

        async def factory():
            msg = "should not be called"
            raise AssertionError(msg)

        result = await cache.get_or_set("babytroc:test:cached", ttl=60, factory=factory)
        assert result == '{"cached": true}'
