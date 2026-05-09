from collections.abc import Awaitable, Callable

from redis.asyncio import Redis


class Cache:
    """Base cache interface."""

    async def get(self, key: str) -> bytes | None:
        raise NotImplementedError

    async def set(self, key: str, value: str, ttl: int) -> None:
        raise NotImplementedError

    async def delete(self, *keys: str) -> None:
        raise NotImplementedError

    async def delete_pattern(self, pattern: str) -> None:
        raise NotImplementedError

    async def get_or_set(
        self,
        key: str,
        ttl: int,
        factory: Callable[[], Awaitable[str]],
    ) -> str:
        raise NotImplementedError


class NullCache(Cache):
    """No-op cache for contexts that don't need caching (e.g. seed scripts)."""

    async def get(self, key: str) -> bytes | None:
        return None

    async def set(self, key: str, value: str, ttl: int) -> None:
        pass

    async def delete(self, *keys: str) -> None:
        pass

    async def delete_pattern(self, pattern: str) -> None:
        pass

    async def get_or_set(
        self,
        key: str,
        ttl: int,
        factory: Callable[[], Awaitable[str]],
    ) -> str:
        return await factory()


class RedisCache(Cache):
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get(self, key: str) -> bytes | None:
        return await self._redis.get(key)

    async def set(self, key: str, value: str, ttl: int) -> None:
        await self._redis.set(key, value, ex=ttl)

    async def delete(self, *keys: str) -> None:
        if keys:
            await self._redis.delete(*keys)

    async def delete_pattern(self, pattern: str) -> None:
        cursor = 0
        while True:
            cursor, keys = await self._redis.scan(
                cursor=cursor, match=pattern, count=100
            )
            if keys:
                await self._redis.delete(*keys)
            if cursor == 0:
                break

    async def get_or_set(
        self,
        key: str,
        ttl: int,
        factory: Callable[[], Awaitable[str]],
    ) -> str:
        cached = await self.get(key)
        if cached is not None:
            return cached.decode()
        value = await factory()
        await self.set(key, value, ttl)
        return value
