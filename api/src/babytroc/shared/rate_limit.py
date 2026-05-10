from datetime import timedelta
from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis

from babytroc.infrastructure.redis_dep import get_redis
from babytroc.routers.v1.auth.verification import maybe_verify_request_credentials
from babytroc.shared.errors import TooManyRequestsError


class RateLimiter:
    """Reusable Redis fixed-window rate limiter usable as a FastAPI dependency.

    Keys are namespaced by prefix and identity:
      ratelimit:{prefix}:user:{client_id}   when authenticated
      ratelimit:{prefix}:ip:{client_host}   when anonymous

    First hit in a window sets EXPIRE. Strict greater-than triggers 429.
    """

    def __init__(
        self,
        *,
        key_prefix: str,
        anon_limit: int,
        auth_limit: int,
        window: timedelta,
    ) -> None:
        self.key_prefix = key_prefix
        self.anon_limit = anon_limit
        self.auth_limit = auth_limit
        self.window = window

    async def __call__(
        self,
        request: Request,
        redis: Annotated[Redis, Depends(get_redis)],
        client_id: Annotated[
            int | None, Depends(maybe_verify_request_credentials)
        ] = None,
    ) -> None:
        if client_id is not None:
            key = f"ratelimit:{self.key_prefix}:user:{client_id}"
            limit = self.auth_limit
        else:
            host = request.client.host if request.client else "unknown"
            key = f"ratelimit:{self.key_prefix}:ip:{host}"
            limit = self.anon_limit

        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, int(self.window.total_seconds()))
        if count > limit:
            msg = "RATE_LIMITED"
            raise TooManyRequestsError(msg)
