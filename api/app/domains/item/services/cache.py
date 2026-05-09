from app.cache_keys import (
    key_item,
    key_user,
    key_user_chats,
    key_user_liked_items,
    key_user_saved_items,
    pattern_items_list,
    pattern_user_items,
    pattern_user_loans,
)
from app.clients.cache import Cache


async def invalidate_item_created(cache: Cache, *, owner_id: int) -> None:
    await cache.delete_pattern(pattern_items_list())
    await cache.delete_pattern(pattern_user_items(owner_id))
    await cache.delete(key_user(owner_id))


async def invalidate_item_updated(cache: Cache, *, item_id: int, owner_id: int) -> None:
    await cache.delete(key_item(item_id))
    await cache.delete_pattern(pattern_items_list())
    await cache.delete_pattern(pattern_user_items(owner_id))


async def invalidate_item_deleted(cache: Cache, *, item_id: int, owner_id: int) -> None:
    await cache.delete(key_item(item_id))
    await cache.delete_pattern(pattern_items_list())
    await cache.delete_pattern(pattern_user_items(owner_id))
    await cache.delete_pattern(pattern_user_loans(owner_id))
    await cache.delete(key_user_chats(owner_id))


async def invalidate_item_liked(
    cache: Cache, *, liker_id: int, item_owner_id: int
) -> None:
    await cache.delete(key_user_liked_items(liker_id))
    await cache.delete(key_user(item_owner_id))


async def invalidate_item_saved(cache: Cache, *, saver_id: int) -> None:
    await cache.delete(key_user_saved_items(saver_id))
