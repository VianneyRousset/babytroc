import json
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.cache_keys import (
    TTL_USER_LIKED,
    TTL_USER_SAVED,
    key_user_liked_items,
    key_user_saved_items,
)
from app.domains.item.models import ItemLike, ItemSave

if TYPE_CHECKING:
    from app.infrastructure.cache_client import Cache


async def get_user_liked_item_ids(
    db: AsyncSession,
    user_id: int,
    cache: "Cache | None" = None,
) -> set[int]:
    """Get set of item IDs liked by user."""

    cache_key = key_user_liked_items(user_id)

    if cache is not None:
        cached = await cache.get(cache_key)
        if cached is not None:
            return set(json.loads(cached))

    stmt = select(ItemLike.item_id).where(ItemLike.user_id == user_id)
    result = (await db.execute(stmt)).scalars().all()
    ids = list(result)

    if cache is not None:
        await cache.set(cache_key, json.dumps(ids), ttl=TTL_USER_LIKED)

    return set(ids)


async def get_user_saved_item_ids(
    db: AsyncSession,
    user_id: int,
    cache: "Cache | None" = None,
) -> set[int]:
    """Get set of item IDs saved by user."""

    cache_key = key_user_saved_items(user_id)

    if cache is not None:
        cached = await cache.get(cache_key)
        if cached is not None:
            return set(json.loads(cached))

    stmt = select(ItemSave.item_id).where(ItemSave.user_id == user_id)
    result = (await db.execute(stmt)).scalars().all()
    ids = list(result)

    if cache is not None:
        await cache.set(cache_key, json.dumps(ids), ttl=TTL_USER_SAVED)

    return set(ids)
