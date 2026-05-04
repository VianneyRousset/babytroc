from app.clients.cache import Cache


def get_cache() -> Cache:
    return _cache


_cache: Cache


def init_cache_dependency(cache: Cache) -> None:
    global _cache
    _cache = cache
