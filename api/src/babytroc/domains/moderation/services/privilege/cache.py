from babytroc.infrastructure.cache_client import Cache
from babytroc.infrastructure.cache_keys import (
    key_moderation_privilege_admins,
    key_moderation_privilege_moderators,
    key_user,
)


async def invalidate_privilege(cache: Cache, *, user_id: int) -> None:
    await cache.delete(key_user(user_id))
    await cache.delete(key_moderation_privilege_moderators())
    await cache.delete(key_moderation_privilege_admins())
