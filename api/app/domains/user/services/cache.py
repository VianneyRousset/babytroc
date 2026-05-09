from app.infrastructure.cache_client import Cache
from app.infrastructure.cache_keys import (
    key_user,
    pattern_items_list,
    pattern_user_all,
)


async def invalidate_user_updated(cache: Cache, *, user_id: int) -> None:
    await cache.delete(key_user(user_id))


async def invalidate_user_validated(cache: Cache, *, user_id: int) -> None:
    await cache.delete(key_user(user_id))
    await cache.delete_pattern(pattern_items_list())


async def invalidate_user_deleted(cache: Cache, *, user_id: int) -> None:
    await cache.delete_pattern(pattern_user_all(user_id))
    await cache.delete(key_user(user_id))
    await cache.delete_pattern(pattern_items_list())
