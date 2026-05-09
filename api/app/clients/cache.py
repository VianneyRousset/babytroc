# Compatibility shim — real module has moved to app.infrastructure.cache_client
from app.infrastructure.cache_client import *  # noqa: F401,F403
from app.infrastructure.cache_client import (
    Cache,
    NullCache,
    RedisCache,
)
