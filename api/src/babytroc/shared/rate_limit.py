from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis

from babytroc.infrastructure.config import Config, RateLimitConfig
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


def make_rate_limit_dep(
    *,
    key_prefix: str,
    extract_config: Callable[[Config], RateLimitConfig],
) -> Callable[..., Awaitable[None]]:
    """Build a FastAPI dependency that applies a per-endpoint rate limit.

    `extract_config` pulls the relevant `RateLimitConfig` out of the global
    `Config` (e.g. `lambda c: c.signup` or `lambda c: c.contact.rate_limit`),
    keeping the factory agnostic to whether the config is flat or nested.

    `key_prefix` is the Redis key namespace and doubles as the cache key on
    `app.state` so each endpoint reuses its own lazily-built limiter.
    """
    cache_attr = f"_rate_limiter_{key_prefix}"

    async def dep(
        request: Request,
        redis: Annotated[Redis, Depends(get_redis)],
        client_id: Annotated[
            int | None, Depends(maybe_verify_request_credentials)
        ] = None,
    ) -> None:
        limiter = getattr(request.app.state, cache_attr, None)
        if limiter is None:
            config: Config = request.app.state.config
            rl_config = extract_config(config)
            limiter = RateLimiter(
                key_prefix=key_prefix,
                anon_limit=rl_config.anon,
                auth_limit=rl_config.auth,
                window=rl_config.window,
            )
            setattr(request.app.state, cache_attr, limiter)
        await limiter(request=request, redis=redis, client_id=client_id)

    return dep
