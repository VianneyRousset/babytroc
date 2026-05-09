from app.cache_keys import (
    key_item,
    key_user_chats,
    pattern_chat_messages,
    pattern_items_list,
    pattern_user_borrowings,
    pattern_user_loans,
)
from app.clients.cache import Cache


async def invalidate_loan_request_created(
    cache: Cache,
    *,
    item_id: int,
    borrower_id: int,
    owner_id: int,
) -> None:
    await cache.delete(key_item(item_id))
    await cache.delete_pattern(pattern_user_borrowings(borrower_id))
    await cache.delete_pattern(pattern_user_loans(owner_id))
    await cache.delete(key_user_chats(owner_id))
    await cache.delete(key_user_chats(borrower_id))
    await cache.delete_pattern(pattern_chat_messages(item_id, borrower_id))


async def invalidate_loan_request_state_changed(
    cache: Cache,
    *,
    item_id: int,
    borrower_id: int,
    owner_id: int,
) -> None:
    await cache.delete(key_item(item_id))
    await cache.delete_pattern(pattern_user_borrowings(borrower_id))
    await cache.delete_pattern(pattern_user_loans(owner_id))
    await cache.delete_pattern(pattern_chat_messages(item_id, borrower_id))


async def invalidate_loan_started(
    cache: Cache,
    *,
    item_id: int,
    borrower_id: int,
    owner_id: int,
) -> None:
    await cache.delete(key_item(item_id))
    await cache.delete_pattern(pattern_items_list())
    await cache.delete_pattern(pattern_user_borrowings(borrower_id))
    await cache.delete_pattern(pattern_user_loans(owner_id))
    await cache.delete_pattern(pattern_chat_messages(item_id, borrower_id))


async def invalidate_loan_ended(
    cache: Cache,
    *,
    item_id: int,
    borrower_id: int,
    owner_id: int,
) -> None:
    await cache.delete(key_item(item_id))
    await cache.delete_pattern(pattern_items_list())
    await cache.delete_pattern(pattern_user_borrowings(borrower_id))
    await cache.delete_pattern(pattern_user_loans(owner_id))
    await cache.delete_pattern(pattern_chat_messages(item_id, borrower_id))
