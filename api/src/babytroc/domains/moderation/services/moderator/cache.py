from babytroc.infrastructure.cache_client import Cache
from babytroc.infrastructure.cache_keys import key_moderation_all_moderators


async def invalidate_list_all_moderators(cache: Cache) -> None:
    await cache.delete(key_moderation_all_moderators())
