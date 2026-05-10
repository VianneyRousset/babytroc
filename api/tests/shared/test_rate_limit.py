from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import Request

from babytroc.shared.errors import TooManyRequestsError
from babytroc.shared.rate_limit import RateLimiter


def _make_request(host: str = "1.2.3.4") -> Request:
    """Build a minimal Starlette Request with a client host."""
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/",
        "headers": [],
        "client": (host, 12345),
        "app": MagicMock(),
    }
    return Request(scope=scope)


class TestRateLimiter:
    def test_init_stores_params(self):
        rl = RateLimiter(
            key_prefix="contact",
            anon_limit=5,
            auth_limit=10,
            window=timedelta(seconds=60),
        )
        assert rl.key_prefix == "contact"
        assert rl.anon_limit == 5
        assert rl.auth_limit == 10
        assert rl.window == timedelta(seconds=60)

    async def test_anon_first_hit_sets_expiry(self):
        redis = AsyncMock()
        redis.incr = AsyncMock(return_value=1)
        redis.expire = AsyncMock()
        rl = RateLimiter(
            key_prefix="contact",
            anon_limit=5,
            auth_limit=10,
            window=timedelta(seconds=60),
        )
        await rl(request=_make_request("9.9.9.9"), redis=redis, client_id=None)
        redis.incr.assert_awaited_once_with("ratelimit:contact:ip:9.9.9.9")
        redis.expire.assert_awaited_once_with("ratelimit:contact:ip:9.9.9.9", 60)

    async def test_anon_subsequent_hit_skips_expire(self):
        redis = AsyncMock()
        redis.incr = AsyncMock(return_value=2)
        redis.expire = AsyncMock()
        rl = RateLimiter(
            key_prefix="contact",
            anon_limit=5,
            auth_limit=10,
            window=timedelta(seconds=60),
        )
        await rl(request=_make_request(), redis=redis, client_id=None)
        redis.expire.assert_not_called()

    async def test_anon_over_limit_raises_429(self):
        redis = AsyncMock()
        redis.incr = AsyncMock(return_value=6)
        redis.expire = AsyncMock()
        rl = RateLimiter(
            key_prefix="contact",
            anon_limit=5,
            auth_limit=10,
            window=timedelta(seconds=60),
        )
        with pytest.raises(TooManyRequestsError) as excinfo:
            await rl(request=_make_request(), redis=redis, client_id=None)
        assert excinfo.value.message == "RATE_LIMITED"

    async def test_auth_uses_user_key_and_auth_limit(self):
        redis = AsyncMock()
        redis.incr = AsyncMock(return_value=10)
        redis.expire = AsyncMock()
        rl = RateLimiter(
            key_prefix="contact",
            anon_limit=5,
            auth_limit=10,
            window=timedelta(seconds=60),
        )
        # 10 == auth_limit → still allowed (strict greater-than triggers 429)
        await rl(request=_make_request(), redis=redis, client_id=42)
        redis.incr.assert_awaited_once_with("ratelimit:contact:user:42")

    async def test_auth_over_limit_raises_429(self):
        redis = AsyncMock()
        redis.incr = AsyncMock(return_value=11)
        rl = RateLimiter(
            key_prefix="contact",
            anon_limit=5,
            auth_limit=10,
            window=timedelta(seconds=60),
        )
        with pytest.raises(TooManyRequestsError):
            await rl(request=_make_request(), redis=redis, client_id=42)

    async def test_anon_and_auth_keys_are_isolated(self):
        """Same IP, different user_id, must not share counters."""
        redis = AsyncMock()
        redis.incr = AsyncMock(return_value=1)
        redis.expire = AsyncMock()
        rl = RateLimiter(
            key_prefix="contact",
            anon_limit=5,
            auth_limit=10,
            window=timedelta(seconds=60),
        )
        await rl(request=_make_request("1.1.1.1"), redis=redis, client_id=None)
        await rl(request=_make_request("1.1.1.1"), redis=redis, client_id=7)
        keys = [c.args[0] for c in redis.incr.await_args_list]
        assert keys == ["ratelimit:contact:ip:1.1.1.1", "ratelimit:contact:user:7"]
