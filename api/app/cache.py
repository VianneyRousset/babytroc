# Compatibility shim — real module has moved to app.infrastructure.cache
from app.infrastructure.cache import *  # noqa: F401,F403
from app.infrastructure.cache import (
    get_cache,
    init_cache_dependency,
)
