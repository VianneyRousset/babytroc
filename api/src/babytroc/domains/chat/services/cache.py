from babytroc.infrastructure.cache_client import Cache
from babytroc.infrastructure.cache_keys import key_user_chats, pattern_chat_messages


async def invalidate_chat_message_sent(
    cache: Cache,
    *,
    item_id: int,
    borrower_id: int,
    owner_id: int,
) -> None:
    await cache.delete(key_user_chats(owner_id))
    await cache.delete(key_user_chats(borrower_id))
    await cache.delete_pattern(pattern_chat_messages(item_id, borrower_id))


async def invalidate_chat_message_seen(
    cache: Cache,
    *,
    item_id: int,
    borrower_id: int,
) -> None:
    await cache.delete_pattern(pattern_chat_messages(item_id, borrower_id))
