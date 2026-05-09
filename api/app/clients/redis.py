# Compatibility shim — real module has moved to app.infrastructure.redis
from app.infrastructure.redis import *  # noqa: F401,F403
from app.infrastructure.redis import create_redis_client
