from app.domains.item.events import (
    ItemCreated,
    ItemDeleted,
    ItemLiked,
    ItemSaved,
    ItemUnliked,
    ItemUnsaved,
    ItemUpdated,
)
from app.infrastructure.events import on


@on(ItemCreated, critical=False)
async def invalidate_cache_on_item_created(db, event: ItemCreated):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_created

    await invalidate_item_created(get_cache(), owner_id=event.owner_id)


@on(ItemUpdated, critical=False)
async def invalidate_cache_on_item_updated(db, event: ItemUpdated):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_updated

    await invalidate_item_updated(get_cache(), item_id=event.item_id, owner_id=event.owner_id)


@on(ItemDeleted, critical=False)
async def invalidate_cache_on_item_deleted(db, event: ItemDeleted):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_deleted

    await invalidate_item_deleted(get_cache(), item_id=event.item_id, owner_id=event.owner_id)


@on(ItemLiked, critical=False)
async def invalidate_cache_on_item_liked(db, event: ItemLiked):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_liked

    await invalidate_item_liked(get_cache(), liker_id=event.user_id, item_owner_id=event.item_owner_id)


@on(ItemUnliked, critical=False)
async def invalidate_cache_on_item_unliked(db, event: ItemUnliked):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_liked

    await invalidate_item_liked(get_cache(), liker_id=event.user_id, item_owner_id=event.item_owner_id)


@on(ItemSaved, critical=False)
async def invalidate_cache_on_item_saved(db, event: ItemSaved):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_saved

    await invalidate_item_saved(get_cache(), saver_id=event.user_id)


@on(ItemUnsaved, critical=False)
async def invalidate_cache_on_item_unsaved(db, event: ItemUnsaved):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_saved

    await invalidate_item_saved(get_cache(), saver_id=event.user_id)
