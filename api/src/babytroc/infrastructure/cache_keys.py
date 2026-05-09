import hashlib
import json

# --- TTL constants (seconds) ---
TTL_CATEGORIES = 86400  # 24h
TTL_REGIONS = 86400  # 24h
TTL_ITEM = 600  # 10min
TTL_ITEMS_LIST = 120  # 2min
TTL_USER = 1800  # 30min
TTL_USER_LIKED = 300  # 5min
TTL_USER_SAVED = 300  # 5min
TTL_USER_ITEMS = 300  # 5min
TTL_USER_CHATS = 120  # 2min
TTL_CHAT_MESSAGES = 120  # 2min
TTL_USER_LOANS = 300  # 5min
TTL_USER_BORROWINGS = 300  # 5min


def cache_key_hash(**params: object) -> str:
    filtered = {k: v for k, v in sorted(params.items()) if v is not None}
    raw = json.dumps(filtered, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# --- Key builders ---

def key_categories() -> str:
    return "babytroc:categories"


def key_regions() -> str:
    return "babytroc:regions"


def key_item(item_id: int) -> str:
    return f"babytroc:item:{item_id}"


def key_items_list(**query_params: object) -> str:
    return f"babytroc:items:list:{cache_key_hash(**query_params)}"


def key_user(user_id: int) -> str:
    return f"babytroc:user:{user_id}"


def key_user_liked_items(user_id: int) -> str:
    return f"babytroc:user:{user_id}:liked_items"


def key_user_saved_items(user_id: int) -> str:
    return f"babytroc:user:{user_id}:saved_items"


def key_user_chats(user_id: int) -> str:
    return f"babytroc:user:{user_id}:chats"


# --- Pattern builders (for invalidation) ---

def pattern_items_list() -> str:
    return "babytroc:items:list:*"


def pattern_user_items(user_id: int) -> str:
    return f"babytroc:user:{user_id}:items:*"


def pattern_user_loans(user_id: int) -> str:
    return f"babytroc:user:{user_id}:loans:*"


def pattern_user_borrowings(user_id: int) -> str:
    return f"babytroc:user:{user_id}:borrowings:*"


def pattern_chat_messages(item_id: int, borrower_id: int) -> str:
    return f"babytroc:chat:{item_id}_{borrower_id}:messages:*"


def pattern_user_all(user_id: int) -> str:
    return f"babytroc:user:{user_id}:*"
