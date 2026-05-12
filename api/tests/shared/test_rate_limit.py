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


class TestMakeRateLimitDep:
    def test_factory_returns_awaitable_dep(self):
        from datetime import timedelta
        from inspect import iscoroutinefunction

        from babytroc.infrastructure.config import RateLimitConfig
        from babytroc.shared.rate_limit import make_rate_limit_dep

        rl_config = RateLimitConfig(
            anon=2, auth=5, window=timedelta(seconds=60),
        )

        dep = make_rate_limit_dep(
            key_prefix="signup",
            extract_config=lambda c: c.signup,
        )
        assert iscoroutinefunction(dep)

    async def test_factory_caches_limiter_on_app_state(self):
        from datetime import timedelta
        from unittest.mock import AsyncMock, MagicMock

        from babytroc.infrastructure.config import RateLimitConfig
        from babytroc.shared.rate_limit import make_rate_limit_dep

        rl_config = RateLimitConfig(
            anon=2, auth=5, window=timedelta(seconds=60),
        )

        # Use a real object for app state to allow getattr/setattr
        class AppState:
            pass

        app_state = AppState()
        app_state.config = MagicMock()
        app_state.config.signup = rl_config

        class App:
            def __init__(self, state):
                self.state = state

        app = App(app_state)

        scope = {
            "type": "http", "method": "POST", "path": "/",
            "headers": [], "client": ("1.2.3.4", 12345),
            "app": app,
        }
        request = Request(scope=scope)
        redis = AsyncMock()
        redis.incr = AsyncMock(return_value=1)
        redis.expire = AsyncMock()

        dep = make_rate_limit_dep(
            key_prefix="signup",
            extract_config=lambda c: c.signup,
        )
        # First call creates and caches the limiter
        await dep(request=request, redis=redis, client_id=None)
        assert hasattr(app_state, "_rate_limiter_signup")

        # Second call reuses the cached limiter (no exception)
        await dep(request=request, redis=redis, client_id=None)
        # Both calls should have incremented redis (2 total calls to incr)
        assert redis.incr.await_count == 2
