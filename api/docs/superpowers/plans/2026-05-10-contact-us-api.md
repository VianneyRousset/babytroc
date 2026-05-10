# Contact Us API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `POST /api/v1/utils/contact` that forwards a contact-form submission by email to `CONTACT_EMAIL`, defended by honeypot + reusable Redis rate-limiter + external `cap` PoW captcha. Anonymous and authenticated users supported. No DB persistence.

**Architecture:** New stateless endpoint under `routers/v1/utils/` package (promoted from `utils.py`). New infrastructure modules: `cap.py` (httpx client to external cap server), `email_contact.py` (fastapi-mail sender). Reusable `RateLimiter` dep class in `shared/rate_limit.py` keyed by `user_id` if authenticated else `client_host`. New env-driven `ContactConfig` and `CapConfig` in `infrastructure/config.py`. `babycli check cap` added.

**Tech Stack:** FastAPI, pydantic, fastapi-mail, httpx (already deps), redis-asyncio, pytest-asyncio.

**Spec:** `docs/superpowers/specs/2026-05-10-contact-us-api-design.md`

---

## File Structure

**New files:**
- `src/babytroc/shared/rate_limit.py` — `RateLimiter` dep class
- `src/babytroc/infrastructure/cap.py` — `verify_cap_token()`
- `src/babytroc/infrastructure/email_contact.py` — `send_contact_email()`
- `src/babytroc/routers/v1/utils/__init__.py` — aggregating router (replaces `utils.py`)
- `src/babytroc/routers/v1/utils/regions.py` — extracted from `utils.py`
- `src/babytroc/routers/v1/utils/categories.py` — extracted from `utils.py`
- `src/babytroc/routers/v1/utils/contact.py` — POST `/utils/contact` handler + schema
- `tests/fixtures/contact.py` — cap stub + tight-rate-limit fixtures
- `tests/shared/__init__.py` and `tests/shared/test_rate_limit.py`
- `tests/infrastructure/test_cap.py`
- `tests/infrastructure/test_email_contact.py`
- `tests/utils/__init__.py` and `tests/utils/test_contact.py`

**Modified files:**
- `src/babytroc/infrastructure/config.py` — add `ContactConfig`, `CapConfig`, attach to `Config`
- `src/babytroc/shared/errors.py` — add `TooManyRequestsError`
- `src/babytroc/app.py` — config wired to app state (no behavior change beyond passing existing fields)
- `src/babycli/check.py` — add `check_cap()` + `cap` subcommand + add `CONTACT_EMAIL` to required vars
- `tests/conftest.py` — register `tests.fixtures.contact` plugin
- `tests/fixtures/app.py` — provide test `ContactConfig` + `CapConfig` defaults
- `tests/babycli/test_check.py` — tests for `check_cap`

**Deleted files:**
- `src/babytroc/routers/v1/utils.py` (replaced by `utils/` package)

---

## Task 1: Add `ContactConfig` and `CapConfig`

**Files:**
- Modify: `src/babytroc/infrastructure/config.py`
- Test: `tests/test_config.py` (create if missing — check first)

- [ ] **Step 1: Check whether a config test file exists**

Run: `ls tests/test_config.py 2>/dev/null || echo MISSING`

If `MISSING`, create the file in step 2 with the test below. Otherwise append the new tests to it.

- [ ] **Step 2: Write failing tests for `ContactConfig.from_env`**

Add to `tests/test_config.py`:

```python
from datetime import timedelta
from unittest.mock import patch

import pytest

from babytroc.infrastructure.config import CapConfig, ContactConfig


class TestContactConfig:
    def test_from_env_with_all_vars(self):
        env = {
            "CONTACT_EMAIL": "contact@babytroc.ch",
            "CONTACT_RATE_LIMIT_ANON": "3",
            "CONTACT_RATE_LIMIT_AUTH": "8",
            "CONTACT_RATE_LIMIT_WINDOW_SECONDS": "600",
        }
        with patch.dict("os.environ", env, clear=True):
            cfg = ContactConfig.from_env()
        assert cfg.email == "contact@babytroc.ch"
        assert cfg.rate_limit_anon == 3
        assert cfg.rate_limit_auth == 8
        assert cfg.rate_limit_window == timedelta(seconds=600)

    def test_from_env_uses_defaults(self):
        env = {"CONTACT_EMAIL": "contact@babytroc.ch"}
        with patch.dict("os.environ", env, clear=True):
            cfg = ContactConfig.from_env()
        assert cfg.rate_limit_anon == 5
        assert cfg.rate_limit_auth == 10
        assert cfg.rate_limit_window == timedelta(seconds=3600)

    def test_from_env_requires_email(self):
        with patch.dict("os.environ", {}, clear=True), pytest.raises(KeyError):
            ContactConfig.from_env()


class TestCapConfig:
    def test_from_env_with_all_vars(self):
        env = {
            "CAP_API_URL": "https://cap.example.com",
            "CAP_SITE_KEY": "site-123",
            "CAP_SECRET_KEY": "secret-xyz",
        }
        with patch.dict("os.environ", env, clear=True):
            cfg = CapConfig.from_env()
        assert cfg.api_url == "https://cap.example.com"
        assert cfg.site_key == "site-123"
        assert cfg.secret_key == "secret-xyz"

    def test_from_env_requires_all_vars(self):
        with patch.dict("os.environ", {}, clear=True), pytest.raises(KeyError):
            CapConfig.from_env()
```

- [ ] **Step 3: Run tests to verify failure**

Run: `pytest tests/test_config.py -v`
Expected: FAIL — `ImportError: cannot import name 'ContactConfig'`.

- [ ] **Step 4: Implement `ContactConfig` and `CapConfig` in `src/babytroc/infrastructure/config.py`**

Append to `src/babytroc/infrastructure/config.py` (after `AuthConfig`, before `Config`):

```python
class ContactConfig(NamedTuple):
    email: str
    rate_limit_anon: int
    rate_limit_auth: int
    rate_limit_window: timedelta

    @classmethod
    def from_env(
        cls,
        email: str | None = None,
        rate_limit_anon: int | None = None,
        rate_limit_auth: int | None = None,
        rate_limit_window: timedelta | None = None,
    ) -> Self:
        if email is None:
            email = _env("CONTACT_EMAIL")
        if rate_limit_anon is None:
            rate_limit_anon = int(_env("CONTACT_RATE_LIMIT_ANON", default="5"))
        if rate_limit_auth is None:
            rate_limit_auth = int(_env("CONTACT_RATE_LIMIT_AUTH", default="10"))
        if rate_limit_window is None:
            rate_limit_window = timedelta(
                seconds=int(_env("CONTACT_RATE_LIMIT_WINDOW_SECONDS", default="3600")),
            )
        return cls(
            email=email,
            rate_limit_anon=rate_limit_anon,
            rate_limit_auth=rate_limit_auth,
            rate_limit_window=rate_limit_window,
        )


class CapConfig(NamedTuple):
    api_url: str
    site_key: str
    secret_key: str

    @classmethod
    def from_env(
        cls,
        api_url: str | None = None,
        site_key: str | None = None,
        secret_key: str | None = None,
    ) -> Self:
        if api_url is None:
            api_url = _env("CAP_API_URL")
        if site_key is None:
            site_key = _env("CAP_SITE_KEY")
        if secret_key is None:
            secret_key = _env("CAP_SECRET_KEY")
        return cls(api_url=api_url, site_key=site_key, secret_key=secret_key)
```

Then attach to `Config`. Find:

```python
class Config(NamedTuple):
    host_name: str
    app_name: str
    test: bool
    delay: float
    database: DatabaseConfig
    pubsub: PubsubConfig
    email: EmailConfig
    s3: S3Config
    redis: RedisConfig
    auth: AuthConfig
```

Replace with:

```python
class Config(NamedTuple):
    host_name: str
    app_name: str
    test: bool
    delay: float
    database: DatabaseConfig
    pubsub: PubsubConfig
    email: EmailConfig
    s3: S3Config
    redis: RedisConfig
    auth: AuthConfig
    contact: ContactConfig
    cap: CapConfig
```

In `Config.from_env`, find the `auth` block:

```python
        if auth is None:
            auth = AuthConfig.from_env()
```

After that block, before the final `return cls(...)`, add:

```python
        if contact is None:
            contact = ContactConfig.from_env()

        if cap is None:
            cap = CapConfig.from_env()
```

Add the `contact` and `cap` parameters to `Config.from_env` signature (next to the other optional configs):

```python
        contact: ContactConfig | None = None,
        cap: CapConfig | None = None,
```

And add them to the final `return cls(...)`:

```python
            contact=contact,
            cap=cap,
```

- [ ] **Step 5: Run tests to verify pass**

Run: `pytest tests/test_config.py -v`
Expected: PASS.

- [ ] **Step 6: Run full lint to catch type errors**

Run: `mise run lint`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/babytroc/infrastructure/config.py tests/test_config.py
git commit -m "feat(config): add ContactConfig and CapConfig with env defaults"
```

---

## Task 2: Wire test fixtures for `ContactConfig` and `CapConfig`

The session-scoped `app_config` fixture builds a `Config` from env. Tests must run without the new env vars set. We provide test defaults in `tests/fixtures/app.py`.

**Files:**
- Modify: `tests/fixtures/app.py`

- [ ] **Step 1: Update `app_config` fixture to inject test `ContactConfig` and `CapConfig`**

Find in `tests/fixtures/app.py`:

```python
from babytroc.infrastructure.config import (
    Config,
    DatabaseConfig,
    PubsubConfig,
    RedisConfig,
    S3Config,
)
```

Replace with:

```python
from datetime import timedelta

from babytroc.infrastructure.config import (
    CapConfig,
    Config,
    ContactConfig,
    DatabaseConfig,
    PubsubConfig,
    RedisConfig,
    S3Config,
)
```

Find:

```python
    return Config.from_env(
        database=DatabaseConfig.from_env(url=primary_database),
        pubsub=PubsubConfig(url=redis_config.url),
        redis=redis_config,
        s3=S3Config(
            endpoint_url="http://localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket="test-bucket",
            public_url="http://localhost:9000/test-bucket",
        ),
    )
```

Replace with:

```python
    return Config.from_env(
        database=DatabaseConfig.from_env(url=primary_database),
        pubsub=PubsubConfig(url=redis_config.url),
        redis=redis_config,
        s3=S3Config(
            endpoint_url="http://localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket="test-bucket",
            public_url="http://localhost:9000/test-bucket",
        ),
        contact=ContactConfig(
            email="test-contact@babytroc.ch",
            rate_limit_anon=5,
            rate_limit_auth=10,
            rate_limit_window=timedelta(seconds=3600),
        ),
        cap=CapConfig(
            api_url="https://cap.test.invalid",
            site_key="test-site-key",
            secret_key="test-secret-key",
        ),
    )
```

- [ ] **Step 2: Run smoke tests to verify nothing broke**

Run: `pytest tests/babycli/test_smoke.py tests/test_utils.py -v`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/fixtures/app.py
git commit -m "test(fixtures): inject ContactConfig and CapConfig into app_config"
```

---

## Task 3: Add `TooManyRequestsError`

**Files:**
- Modify: `src/babytroc/shared/errors.py`
- Test: `tests/shared/__init__.py` (create) and `tests/shared/test_errors.py`

- [ ] **Step 1: Create empty test package init**

```bash
mkdir -p tests/shared
touch tests/shared/__init__.py
```

- [ ] **Step 2: Write failing test in `tests/shared/test_errors.py`**

```python
from http import HTTPStatus

from babytroc.shared.errors import TooManyRequestsError


def test_too_many_requests_error_status_429():
    err = TooManyRequestsError("RATE_LIMITED")
    assert err.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert err.message == "RATE_LIMITED"


def test_too_many_requests_error_passes_headers():
    err = TooManyRequestsError("RATE_LIMITED", headers={"Retry-After": "60"})
    assert err.headers == {"Retry-After": "60"}
```

- [ ] **Step 3: Run test to verify failure**

Run: `pytest tests/shared/test_errors.py -v`
Expected: FAIL — `ImportError: cannot import name 'TooManyRequestsError'`.

- [ ] **Step 4: Implement `TooManyRequestsError`**

Append to `src/babytroc/shared/errors.py`:

```python
class TooManyRequestsError(ApiError):
    """Client exceeded a rate limit."""

    def __init__(
        self,
        message: str,
        **kwargs,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            **kwargs,
        )
```

- [ ] **Step 5: Run test to verify pass**

Run: `pytest tests/shared/test_errors.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/babytroc/shared/errors.py tests/shared/__init__.py tests/shared/test_errors.py
git commit -m "feat(errors): add TooManyRequestsError for 429 responses"
```

---

## Task 4: Reusable `RateLimiter` dep

The limiter uses Redis directly via `app.state.redis` (a `redis.asyncio.Redis` client). The existing `Cache` interface lacks `INCR`/`EXPIRE`, so we add a small dependency `get_redis` that returns the raw client.

**Files:**
- Create: `src/babytroc/infrastructure/redis_dep.py`
- Create: `src/babytroc/shared/rate_limit.py`
- Test: `tests/shared/test_rate_limit.py`

- [ ] **Step 1: Add `get_redis` request-scoped dependency**

Create `src/babytroc/infrastructure/redis_dep.py`:

```python
from fastapi import Request
from redis.asyncio import Redis


def get_redis(request: Request) -> Redis:
    return request.app.state.redis
```

- [ ] **Step 2: Write failing tests for `RateLimiter`**

`tests/shared/test_rate_limit.py`:

```python
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
```

- [ ] **Step 3: Run tests to verify failure**

Run: `pytest tests/shared/test_rate_limit.py -v`
Expected: FAIL — `ImportError: cannot import name 'RateLimiter'`.

- [ ] **Step 4: Implement `RateLimiter`**

`src/babytroc/shared/rate_limit.py`:

```python
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
            raise TooManyRequestsError("RATE_LIMITED")
```

- [ ] **Step 5: Run tests to verify pass**

Run: `pytest tests/shared/test_rate_limit.py -v`
Expected: PASS.

- [ ] **Step 6: Run lint**

Run: `mise run lint`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/babytroc/infrastructure/redis_dep.py src/babytroc/shared/rate_limit.py tests/shared/test_rate_limit.py
git commit -m "feat(shared): add reusable Redis-backed RateLimiter dep"
```

---

## Task 5: `verify_cap_token` cap client

**Files:**
- Create: `src/babytroc/infrastructure/cap.py`
- Test: `tests/infrastructure/test_cap.py`

- [ ] **Step 1: Write failing tests using httpx MockTransport**

`tests/infrastructure/test_cap.py`:

```python
import httpx
import pytest

from babytroc.infrastructure.cap import verify_cap_token
from babytroc.infrastructure.config import CapConfig


CONFIG = CapConfig(
    api_url="https://cap.example.com",
    site_key="site-1",
    secret_key="secret-1",
)


def _client_with(transport: httpx.MockTransport) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=transport, timeout=5.0)


async def test_verify_cap_token_returns_true_on_success(monkeypatch):
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = request.read()
        return httpx.Response(200, json={"success": True})

    monkeypatch.setattr(
        "babytroc.infrastructure.cap.httpx.AsyncClient",
        lambda *a, **kw: _client_with(httpx.MockTransport(handler)),
    )
    assert await verify_cap_token(CONFIG, "token-abc") is True
    assert captured["url"] == "https://cap.example.com/site-1/siteverify"
    assert b"secret-1" in captured["body"]
    assert b"token-abc" in captured["body"]


async def test_verify_cap_token_returns_false_on_success_false(monkeypatch):
    def handler(request):
        return httpx.Response(200, json={"success": False})

    monkeypatch.setattr(
        "babytroc.infrastructure.cap.httpx.AsyncClient",
        lambda *a, **kw: _client_with(httpx.MockTransport(handler)),
    )
    assert await verify_cap_token(CONFIG, "bad-token") is False


async def test_verify_cap_token_returns_false_on_non_200(monkeypatch):
    def handler(request):
        return httpx.Response(500, json={"error": "boom"})

    monkeypatch.setattr(
        "babytroc.infrastructure.cap.httpx.AsyncClient",
        lambda *a, **kw: _client_with(httpx.MockTransport(handler)),
    )
    assert await verify_cap_token(CONFIG, "token") is False


async def test_verify_cap_token_returns_false_on_network_error(monkeypatch):
    def handler(request):
        raise httpx.ConnectError("server unreachable")

    monkeypatch.setattr(
        "babytroc.infrastructure.cap.httpx.AsyncClient",
        lambda *a, **kw: _client_with(httpx.MockTransport(handler)),
    )
    assert await verify_cap_token(CONFIG, "token") is False


async def test_verify_cap_token_returns_false_on_invalid_json(monkeypatch):
    def handler(request):
        return httpx.Response(200, content=b"not json")

    monkeypatch.setattr(
        "babytroc.infrastructure.cap.httpx.AsyncClient",
        lambda *a, **kw: _client_with(httpx.MockTransport(handler)),
    )
    assert await verify_cap_token(CONFIG, "token") is False
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/infrastructure/test_cap.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Implement `verify_cap_token`**

`src/babytroc/infrastructure/cap.py`:

```python
import httpx

from babytroc.infrastructure.config import CapConfig


async def verify_cap_token(config: CapConfig, token: str) -> bool:
    """Verify a cap PoW token by calling the cap server's /siteverify endpoint.

    Returns False on any failure (HTTP non-200, network error, success=False,
    invalid JSON). Failure is fail-closed by design — see spec.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{config.api_url}/{config.site_key}/siteverify",
                json={"secret": config.secret_key, "response": token},
            )
            if resp.status_code != 200:
                return False
            try:
                payload = resp.json()
            except ValueError:
                return False
            return payload.get("success") is True
    except httpx.HTTPError:
        return False
```

- [ ] **Step 4: Run tests to verify pass**

Run: `pytest tests/infrastructure/test_cap.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/babytroc/infrastructure/cap.py tests/infrastructure/test_cap.py
git commit -m "feat(cap): add httpx client for cap PoW captcha siteverify"
```

---

## Task 6: `send_contact_email` sender

**Files:**
- Create: `src/babytroc/infrastructure/email_contact.py`
- Test: `tests/infrastructure/test_email_contact.py`

- [ ] **Step 1: Write failing tests using `FastMail.record_messages`**

`tests/infrastructure/test_email_contact.py`:

```python
from fastapi_mail import ConnectionConfig, FastMail
from pydantic import SecretStr

from babytroc.infrastructure.email_contact import send_contact_email


def _fastmail() -> FastMail:
    return FastMail(
        ConnectionConfig(
            MAIL_USERNAME="u",
            MAIL_PASSWORD=SecretStr("p"),
            MAIL_PORT=587,
            MAIL_SERVER="smtp.test",
            MAIL_FROM="noreply@test",
            MAIL_FROM_NAME="Test",
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=False,
            SUPPRESS_SEND=1,
        )
    )


async def test_send_contact_email_recipient_is_contact_email():
    client = _fastmail()
    async with client.record_messages() as outbox:
        await send_contact_email(
            client,
            app_name="Babytroc",
            contact_email="contact@babytroc.ch",
            submitter_name="Alice",
            submitter_email="alice@example.com",
            subject="Hello",
            message="Hi there",
            authenticated_user_id=None,
        )
    assert len(outbox) == 1
    msg = outbox[0]
    assert "contact@babytroc.ch" in msg["To"]


async def test_send_contact_email_subject_has_app_prefix():
    client = _fastmail()
    async with client.record_messages() as outbox:
        await send_contact_email(
            client,
            app_name="Babytroc",
            contact_email="contact@babytroc.ch",
            submitter_name="Alice",
            submitter_email="alice@example.com",
            subject="Question",
            message="Hi",
            authenticated_user_id=None,
        )
    assert outbox[0]["Subject"] == "[Babytroc] Contact: Question"


async def test_send_contact_email_reply_to_set_to_submitter():
    client = _fastmail()
    async with client.record_messages() as outbox:
        await send_contact_email(
            client,
            app_name="Babytroc",
            contact_email="contact@babytroc.ch",
            submitter_name="Alice",
            submitter_email="alice@example.com",
            subject="x",
            message="y",
            authenticated_user_id=None,
        )
    assert "alice@example.com" in outbox[0]["Reply-To"]


async def test_send_contact_email_escapes_html_in_message():
    client = _fastmail()
    async with client.record_messages() as outbox:
        await send_contact_email(
            client,
            app_name="Babytroc",
            contact_email="contact@babytroc.ch",
            submitter_name="<b>Eve</b>",
            submitter_email="eve@example.com",
            subject="x",
            message="<script>alert(1)</script>",
            authenticated_user_id=None,
        )
    body = outbox[0].get_payload()
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body
    assert "<b>Eve</b>" not in body
    assert "&lt;b&gt;Eve&lt;/b&gt;" in body


async def test_send_contact_email_renders_user_id_when_authenticated():
    client = _fastmail()
    async with client.record_messages() as outbox:
        await send_contact_email(
            client,
            app_name="Babytroc",
            contact_email="contact@babytroc.ch",
            submitter_name="Alice",
            submitter_email="alice@example.com",
            subject="x",
            message="y",
            authenticated_user_id=42,
        )
    body = outbox[0].get_payload()
    assert "Authenticated user ID:</b> 42" in body


async def test_send_contact_email_renders_dash_when_anonymous():
    client = _fastmail()
    async with client.record_messages() as outbox:
        await send_contact_email(
            client,
            app_name="Babytroc",
            contact_email="contact@babytroc.ch",
            submitter_name="Alice",
            submitter_email="alice@example.com",
            subject="x",
            message="y",
            authenticated_user_id=None,
        )
    body = outbox[0].get_payload()
    assert "Authenticated user ID:</b> —" in body
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/infrastructure/test_email_contact.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Implement `send_contact_email`**

`src/babytroc/infrastructure/email_contact.py`:

```python
from html import escape

from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr, NameEmail


async def send_contact_email(
    email_client: FastMail,
    *,
    app_name: str,
    contact_email: str,
    submitter_name: str,
    submitter_email: EmailStr,
    subject: str,
    message: str,
    authenticated_user_id: int | None,
) -> None:
    """Forward a contact-form submission to the contact mailbox."""
    user_id_str = (
        str(authenticated_user_id) if authenticated_user_id is not None else "—"
    )
    msg = MessageSchema(
        subject=f"[{app_name}] Contact: {subject}",
        recipients=[NameEmail(name="Contact", email=contact_email)],
        reply_to=[NameEmail(name=submitter_name, email=submitter_email)],
        body=(
            "<h2>New contact form submission</h2>"
            f"<p><b>From:</b> {escape(submitter_name)} "
            f"&lt;{escape(submitter_email)}&gt;</p>"
            f"<p><b>Authenticated user ID:</b> {escape(user_id_str)}</p>"
            f"<p><b>Subject:</b> {escape(subject)}</p>"
            "<hr>"
            f"<pre>{escape(message)}</pre>"
        ),
        subtype=MessageType.html,
    )
    await email_client.send_message(msg)
```

- [ ] **Step 4: Run tests to verify pass**

Run: `pytest tests/infrastructure/test_email_contact.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/babytroc/infrastructure/email_contact.py tests/infrastructure/test_email_contact.py
git commit -m "feat(email): add send_contact_email with HTML escaping and reply-to"
```

---

## Task 7: Promote `routers/v1/utils.py` to package (no behavior change)

**Files:**
- Delete: `src/babytroc/routers/v1/utils.py`
- Create: `src/babytroc/routers/v1/utils/__init__.py`
- Create: `src/babytroc/routers/v1/utils/regions.py`
- Create: `src/babytroc/routers/v1/utils/categories.py`

- [ ] **Step 1: Run existing utils tests as baseline**

Run: `pytest tests/test_utils.py -v`
Expected: PASS.

- [ ] **Step 2: Create new package directory**

```bash
mkdir -p src/babytroc/routers/v1/utils
```

- [ ] **Step 3: Create `regions.py`**

`src/babytroc/routers/v1/utils/regions.py`:

```python
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.region import services as region_services
from babytroc.domains.region.schemas.read import RegionRead
from babytroc.infrastructure.cache import get_cache
from babytroc.infrastructure.cache_client import Cache
from babytroc.infrastructure.database import get_db_session

router = APIRouter()


@router.get("/regions", status_code=status.HTTP_200_OK)
async def list_regions(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> list[RegionRead]:
    """List regions."""
    return await region_services.list_regions(db, cache)
```

- [ ] **Step 4: Create `categories.py`**

`src/babytroc/routers/v1/utils/categories.py`:

```python
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.category import services as category_services
from babytroc.domains.category.schemas.read import CategoryRead
from babytroc.infrastructure.cache import get_cache
from babytroc.infrastructure.cache_client import Cache
from babytroc.infrastructure.database import get_db_session

router = APIRouter()


@router.get("/categories", status_code=status.HTTP_200_OK)
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> list[CategoryRead]:
    """List categories."""
    return await category_services.list_categories(db, cache)
```

- [ ] **Step 5: Create aggregating `__init__.py`**

`src/babytroc/routers/v1/utils/__init__.py`:

```python
from fastapi import APIRouter

from . import categories, regions

router = APIRouter()
router.include_router(regions.router)
router.include_router(categories.router)
```

- [ ] **Step 6: Delete old `utils.py`**

```bash
rm src/babytroc/routers/v1/utils.py
```

- [ ] **Step 7: Run baseline tests to verify behavior unchanged**

Run: `pytest tests/test_utils.py -v`
Expected: PASS — same endpoints (`/api/v1/utils/regions`, `/api/v1/utils/categories`) still work.

- [ ] **Step 8: Run lint**

Run: `mise run lint`
Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add src/babytroc/routers/v1/utils tests/test_utils.py
git rm src/babytroc/routers/v1/utils.py 2>/dev/null || true
git commit -m "refactor(routers): promote utils.py to utils/ package"
```

---

## Task 8: `tests/fixtures/contact.py` — cap stub + tight rate-limit override

The `contact` endpoint built in Task 9 will use `verify_cap_token` and a `RateLimiter` instance. Tests need to override both.

**Files:**
- Create: `tests/fixtures/contact.py`
- Modify: `tests/conftest.py`
- Create: `tests/utils/__init__.py`

- [ ] **Step 1: Register the new fixture plugin in `tests/conftest.py`**

Find:

```python
pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.app",
    "tests.fixtures.regions",
    "tests.fixtures.users",
    "tests.fixtures.clients",
    "tests.fixtures.items",
    "tests.fixtures.loans",
    "tests.fixtures.websockets",
    "tests.fixtures.chat",
    "tests.fixtures.categories",
    "tests.fixtures.s3",
]
```

Replace with:

```python
pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.app",
    "tests.fixtures.regions",
    "tests.fixtures.users",
    "tests.fixtures.clients",
    "tests.fixtures.items",
    "tests.fixtures.loans",
    "tests.fixtures.websockets",
    "tests.fixtures.chat",
    "tests.fixtures.categories",
    "tests.fixtures.s3",
    "tests.fixtures.contact",
]
```

- [ ] **Step 2: Create the contact fixtures module**

`tests/fixtures/contact.py`:

```python
from collections.abc import AsyncGenerator, Callable
from datetime import timedelta

import pytest
from fastapi import FastAPI

from babytroc.infrastructure import cap as cap_module
from babytroc.shared.rate_limit import RateLimiter


@pytest.fixture
def cap_verify_result() -> bool:
    """Override in tests via `@pytest.mark.parametrize` or direct fixture override
    to make the stubbed cap verifier return False."""
    return True


@pytest.fixture
def cap_verify_raises() -> bool:
    """Override to make the stubbed cap verifier raise an httpx error path."""
    return False


@pytest.fixture(autouse=True)
def stub_cap_verify(
    monkeypatch: pytest.MonkeyPatch,
    cap_verify_result: bool,
    cap_verify_raises: bool,
):
    """Replace `verify_cap_token` so tests don't reach a real cap server.

    The contact router imports `verify_cap_token` from `babytroc.infrastructure.cap`,
    so we patch the symbol *on the module the router imported it from*. Because
    `babytroc.routers.v1.utils.contact` does `from babytroc.infrastructure.cap import
    verify_cap_token`, we patch both locations.
    """

    async def _fake(_config, _token):
        if cap_verify_raises:
            import httpx

            raise httpx.ConnectError("boom")
        return cap_verify_result

    monkeypatch.setattr(cap_module, "verify_cap_token", _fake)
    # The router binds the symbol at import time; patch its bound reference too
    # if the import has already happened.
    try:
        from babytroc.routers.v1.utils import contact as contact_router_module

        monkeypatch.setattr(contact_router_module, "verify_cap_token", _fake)
    except ImportError:
        pass


@pytest.fixture
def tight_rate_limit_factory(app: FastAPI) -> Callable[[int, int, int], None]:
    """Return a function that overrides the contact rate limiter with tight values
    (short window) so rate-limit tests run fast.

    Usage in a test:
        tight_rate_limit_factory(anon_limit=2, auth_limit=3, window_seconds=60)
    """

    def _set(*, anon_limit: int, auth_limit: int, window_seconds: int) -> None:
        from babytroc.routers.v1.utils.contact import (
            rate_limit_contact as original,
        )

        new = RateLimiter(
            key_prefix="contact-test",
            anon_limit=anon_limit,
            auth_limit=auth_limit,
            window=timedelta(seconds=window_seconds),
        )
        app.dependency_overrides[original] = new

    return _set


@pytest.fixture(autouse=True)
async def _clear_contact_overrides(app: FastAPI) -> AsyncGenerator[None]:
    yield
    # Remove any overrides set by tight_rate_limit_factory after each test.
    try:
        from babytroc.routers.v1.utils.contact import rate_limit_contact

        app.dependency_overrides.pop(rate_limit_contact, None)
    except ImportError:
        pass
```

- [ ] **Step 3: Create empty test package init for `tests/utils`**

```bash
mkdir -p tests/utils
touch tests/utils/__init__.py
```

- [ ] **Step 4: Verify fixtures load by running an unrelated test**

Run: `pytest tests/test_utils.py -v`
Expected: PASS — the autouse fixtures are no-ops when no `contact` import occurs (the `try/except ImportError` swallows the missing module until Task 9 lands).

- [ ] **Step 5: Commit**

```bash
git add tests/conftest.py tests/fixtures/contact.py tests/utils/__init__.py
git commit -m "test(fixtures): add cap stub and rate-limit override for contact"
```

---

## Task 9: Contact endpoint (TDD, full security matrix)

This task assembles the endpoint and validates every security layer with end-to-end tests. We write the tests first as a single batch since they exercise one endpoint together.

**Files:**
- Create: `src/babytroc/routers/v1/utils/contact.py`
- Modify: `src/babytroc/routers/v1/utils/__init__.py` (include the new router)
- Test: `tests/utils/test_contact.py`

- [ ] **Step 1: Write the full failing test suite**

`tests/utils/test_contact.py`:

```python
import pytest
from fastapi import FastAPI
from httpx import AsyncClient


VALID_PAYLOAD = {
    "name": "Alice",
    "email": "alice@example.com",
    "subject": "Hello",
    "message": "Hi there",
    "cap_token": "valid-token",
}


def _payload(**overrides) -> dict:
    return {**VALID_PAYLOAD, **overrides}


# ---- happy paths ----

async def test_anon_valid_submission_returns_204(client: AsyncClient, app: FastAPI):
    async with app.state.email_client.record_messages() as outbox:
        resp = await client.post("/api/v1/utils/contact", json=_payload())
    assert resp.status_code == 204
    assert len(outbox) == 1
    assert "test-contact@babytroc.ch" in outbox[0]["To"]
    assert "Authenticated user ID:</b> —" in outbox[0].get_payload()


async def test_authenticated_submission_includes_user_id(
    alice_client: AsyncClient,
    app: FastAPI,
    alice,
):
    async with app.state.email_client.record_messages() as outbox:
        resp = await alice_client.post("/api/v1/utils/contact", json=_payload())
    assert resp.status_code == 204
    body = outbox[0].get_payload()
    assert f"Authenticated user ID:</b> {alice.id}" in body


# ---- honeypot ----

async def test_honeypot_filled_returns_400_invalid_submission(
    client: AsyncClient, app: FastAPI
):
    async with app.state.email_client.record_messages() as outbox:
        resp = await client.post(
            "/api/v1/utils/contact", json=_payload(website="bot was here"),
        )
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"
    assert outbox == []


# ---- cap layer ----

@pytest.mark.parametrize("cap_verify_result", [False])
async def test_cap_rejected_returns_400_invalid_submission(
    client: AsyncClient, app: FastAPI, cap_verify_result
):
    async with app.state.email_client.record_messages() as outbox:
        resp = await client.post("/api/v1/utils/contact", json=_payload())
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"
    assert outbox == []


@pytest.mark.parametrize("cap_verify_raises", [True])
async def test_cap_unreachable_returns_400_invalid_submission(
    client: AsyncClient, app: FastAPI, cap_verify_raises
):
    async with app.state.email_client.record_messages() as outbox:
        resp = await client.post("/api/v1/utils/contact", json=_payload())
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"
    assert outbox == []


# ---- rate limit ----

async def test_anon_rate_limit_triggers_429(
    client: AsyncClient, tight_rate_limit_factory
):
    tight_rate_limit_factory(anon_limit=2, auth_limit=10, window_seconds=60)
    r1 = await client.post("/api/v1/utils/contact", json=_payload())
    r2 = await client.post("/api/v1/utils/contact", json=_payload())
    r3 = await client.post("/api/v1/utils/contact", json=_payload())
    assert r1.status_code == 204
    assert r2.status_code == 204
    assert r3.status_code == 429
    assert r3.json()["message"] == "RATE_LIMITED"


async def test_auth_rate_limit_triggers_429(
    alice_client: AsyncClient, tight_rate_limit_factory
):
    tight_rate_limit_factory(anon_limit=10, auth_limit=2, window_seconds=60)
    r1 = await alice_client.post("/api/v1/utils/contact", json=_payload())
    r2 = await alice_client.post("/api/v1/utils/contact", json=_payload())
    r3 = await alice_client.post("/api/v1/utils/contact", json=_payload())
    assert r1.status_code == 204
    assert r2.status_code == 204
    assert r3.status_code == 429


async def test_anon_and_auth_quotas_are_isolated(
    client: AsyncClient,
    alice_client: AsyncClient,
    tight_rate_limit_factory,
):
    tight_rate_limit_factory(anon_limit=2, auth_limit=2, window_seconds=60)
    # Use up alice's quota
    assert (await alice_client.post("/api/v1/utils/contact", json=_payload())).status_code == 204
    assert (await alice_client.post("/api/v1/utils/contact", json=_payload())).status_code == 204
    # Anonymous client on same IP should still have its full quota
    assert (await client.post("/api/v1/utils/contact", json=_payload())).status_code == 204
    assert (await client.post("/api/v1/utils/contact", json=_payload())).status_code == 204


# ---- pydantic validation ----

@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("name", ""),
        ("name", "x" * 101),
        ("email", "not-an-email"),
        ("subject", ""),
        ("subject", "x" * 201),
        ("message", ""),
        ("message", "x" * 5001),
    ],
)
async def test_validation_rejects_bad_field(
    client: AsyncClient, field: str, bad_value: str
):
    resp = await client.post(
        "/api/v1/utils/contact", json=_payload(**{field: bad_value}),
    )
    # The app's RequestValidationError handler converts 422 to 400 with detail.
    assert resp.status_code == 400


async def test_validation_rejects_missing_field(client: AsyncClient):
    payload = _payload()
    payload.pop("cap_token")
    resp = await client.post("/api/v1/utils/contact", json=payload)
    assert resp.status_code == 400


# ---- HTML injection safety (also covered at sender unit level; double-check via API) ----

async def test_html_injection_in_message_is_escaped(
    client: AsyncClient, app: FastAPI
):
    async with app.state.email_client.record_messages() as outbox:
        resp = await client.post(
            "/api/v1/utils/contact",
            json=_payload(message="<script>alert(1)</script>"),
        )
    assert resp.status_code == 204
    body = outbox[0].get_payload()
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/utils/test_contact.py -v`
Expected: FAIL — endpoint missing, 404 on every request.

- [ ] **Step 3: Implement the endpoint**

`src/babytroc/routers/v1/utils/contact.py`:

```python
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr, StringConstraints

from redis.asyncio import Redis

from babytroc.infrastructure.cap import verify_cap_token
from babytroc.infrastructure.config import Config
from babytroc.infrastructure.email import get_email_client
from babytroc.infrastructure.email_contact import send_contact_email
from babytroc.infrastructure.redis_dep import get_redis
from babytroc.routers.v1.auth.verification import maybe_verify_request_credentials
from babytroc.shared.errors import BadRequestError
from babytroc.shared.rate_limit import RateLimiter

router = APIRouter()


class ContactSubmit(BaseModel):
    name: Annotated[
        str, StringConstraints(min_length=1, max_length=100, strip_whitespace=True)
    ]
    email: EmailStr
    subject: Annotated[
        str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)
    ]
    message: Annotated[
        str, StringConstraints(min_length=1, max_length=5000, strip_whitespace=True)
    ]
    cap_token: Annotated[str, StringConstraints(min_length=1, max_length=4096)]
    website: str = ""  # honeypot — bots fill, humans don't see


async def rate_limit_contact(
    request: Request,
    redis: Annotated[Redis, Depends(get_redis)],
    client_id: Annotated[int | None, Depends(maybe_verify_request_credentials)],
) -> None:
    """Production rate-limit dep for the contact endpoint.

    Lazily builds and caches a `RateLimiter` from `app.state.config.contact`
    on first invocation per app instance. Tests override this dep entirely
    via `app.dependency_overrides[rate_limit_contact] = <RateLimiter instance>`.
    """
    limiter: RateLimiter | None = getattr(request.app.state, "_contact_limiter", None)
    if limiter is None:
        config: Config = request.app.state.config
        limiter = RateLimiter(
            key_prefix="contact",
            anon_limit=config.contact.rate_limit_anon,
            auth_limit=config.contact.rate_limit_auth,
            window=config.contact.rate_limit_window,
        )
        request.app.state._contact_limiter = limiter
    await limiter(request=request, redis=redis, client_id=client_id)


@router.post("/contact", status_code=status.HTTP_204_NO_CONTENT)
async def submit_contact(
    payload: ContactSubmit,
    request: Request,
    background_tasks: BackgroundTasks,
    _rate_limited: Annotated[None, Depends(rate_limit_contact)],
    client_id: Annotated[int | None, Depends(maybe_verify_request_credentials)],
) -> Response:
    # 1. honeypot
    if payload.website:
        raise BadRequestError("INVALID_SUBMISSION")

    # 2. cap captcha
    config: Config = request.app.state.config
    if not await verify_cap_token(config.cap, payload.cap_token):
        raise BadRequestError("INVALID_SUBMISSION")

    # 3. enqueue email send
    email_client = get_email_client()
    background_tasks.add_task(
        send_contact_email,
        email_client,
        app_name=config.app_name,
        contact_email=config.contact.email,
        submitter_name=payload.name,
        submitter_email=payload.email,
        subject=payload.subject,
        message=payload.message,
        authenticated_user_id=client_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

- [ ] **Step 4: Wire the contact router into the utils package**

Edit `src/babytroc/routers/v1/utils/__init__.py`:

```python
from fastapi import APIRouter

from . import categories, contact, regions

router = APIRouter()
router.include_router(regions.router)
router.include_router(categories.router)
router.include_router(contact.router)
```

- [ ] **Step 5: Run the full contact suite**

Run: `pytest tests/utils/test_contact.py -v`
Expected: PASS for all cases.

- [ ] **Step 6: Run the full utils suite to confirm no regression**

Run: `pytest tests/test_utils.py tests/utils/test_contact.py -v`
Expected: PASS.

- [ ] **Step 7: Run full lint**

Run: `mise run lint`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add src/babytroc/routers/v1/utils/contact.py src/babytroc/routers/v1/utils/__init__.py tests/utils/test_contact.py
git commit -m "feat(api): add POST /v1/utils/contact with honeypot + rate limit + cap"
```

---

## Task 10: `babycli check cap` and `CONTACT_EMAIL` in email check

**Files:**
- Modify: `src/babycli/check.py`
- Modify: `tests/babycli/test_check.py`

- [ ] **Step 1: Write failing tests for `check_cap` and updated `check_email_config`**

Append to `tests/babycli/test_check.py`:

```python
from unittest.mock import patch

import httpx

from babycli.check import check_cap, check_email_config


async def test_check_cap_success(monkeypatch):
    env = {
        "CAP_API_URL": "https://cap.example.com",
        "CAP_SITE_KEY": "site",
        "CAP_SECRET_KEY": "secret",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        "babycli.check.httpx.AsyncClient",
        lambda *a, **kw: httpx.AsyncClient(transport=transport, timeout=5.0),
    )
    with patch.dict("os.environ", env, clear=True):
        result = await check_cap()
    assert result is True


async def test_check_cap_failure_on_network_error(monkeypatch):
    env = {
        "CAP_API_URL": "https://cap.example.com",
        "CAP_SITE_KEY": "site",
        "CAP_SECRET_KEY": "secret",
    }

    def handler(request):
        raise httpx.ConnectError("unreachable")

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        "babycli.check.httpx.AsyncClient",
        lambda *a, **kw: httpx.AsyncClient(transport=transport, timeout=5.0),
    )
    with patch.dict("os.environ", env, clear=True):
        result = await check_cap()
    assert result is False


async def test_check_cap_accepts_non_200():
    """A 404 still proves the cap server is reachable."""
    env = {
        "CAP_API_URL": "https://cap.example.com",
        "CAP_SITE_KEY": "site",
        "CAP_SECRET_KEY": "secret",
    }

    def handler(request):
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    with patch.dict("os.environ", env, clear=True), patch(
        "babycli.check.httpx.AsyncClient",
        lambda *a, **kw: httpx.AsyncClient(transport=transport, timeout=5.0),
    ):
        result = await check_cap()
    assert result is True


def test_check_email_config_requires_contact_email():
    env = {
        "EMAIL_SERVER": "smtp.example.com",
        "EMAIL_PORT": "587",
        "EMAIL_USERNAME": "user",
        "EMAIL_PASSWORD": "pass",
        "EMAIL_FROM_EMAIL": "noreply@example.com",
        "EMAIL_FROM_NAME": "Babytroc",
        # CONTACT_EMAIL deliberately missing
    }
    with patch.dict("os.environ", env, clear=True):
        result = check_email_config()
    assert result is False


def test_check_email_config_passes_with_contact_email():
    env = {
        "EMAIL_SERVER": "smtp.example.com",
        "EMAIL_PORT": "587",
        "EMAIL_USERNAME": "user",
        "EMAIL_PASSWORD": "pass",
        "EMAIL_FROM_EMAIL": "noreply@example.com",
        "EMAIL_FROM_NAME": "Babytroc",
        "CONTACT_EMAIL": "contact@example.com",
    }
    with patch.dict("os.environ", env, clear=True):
        result = check_email_config()
    assert result is True
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/babycli/test_check.py -v`
Expected: FAIL — `check_cap` not defined; existing `test_check_email_config_valid` still passes (legacy env list); new test asserting `CONTACT_EMAIL` requirement fails.

- [ ] **Step 3: Add `httpx` import and `check_cap` in `src/babycli/check.py`**

At the top of `src/babycli/check.py`, add:

```python
import httpx
```

(if not already present.)

After `check_migrations` (and before `@check_app.default async def check_all`), add:

```python
async def check_cap() -> bool:
    try:
        from babytroc.infrastructure.config import CapConfig

        config = CapConfig.from_env()
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get(f"{config.api_url}/", timeout=5.0)
        console_ok(f"Cap — reachable ({config.api_url})")
        return True
    except Exception as e:
        console_err(f"Cap — {e}")
        return False
```

- [ ] **Step 4: Add `CONTACT_EMAIL` to `check_email_config` required list**

Find:

```python
def check_email_config() -> bool:
    required = [
        "EMAIL_SERVER",
        "EMAIL_PORT",
        "EMAIL_USERNAME",
        "EMAIL_PASSWORD",
        "EMAIL_FROM_EMAIL",
        "EMAIL_FROM_NAME",
    ]
```

Replace with:

```python
def check_email_config() -> bool:
    required = [
        "EMAIL_SERVER",
        "EMAIL_PORT",
        "EMAIL_USERNAME",
        "EMAIL_PASSWORD",
        "EMAIL_FROM_EMAIL",
        "EMAIL_FROM_NAME",
        "CONTACT_EMAIL",
    ]
```

- [ ] **Step 5: Wire `check_cap` into `check_all` and add subcommand**

Find:

```python
@check_app.default
async def check_all():
    """Run all health checks."""
    results = [
        await check_postgres(),
        await check_redis(),
        await check_s3(),
        check_email_config(),
        await check_migrations(),
    ]
```

Replace with:

```python
@check_app.default
async def check_all():
    """Run all health checks."""
    results = [
        await check_postgres(),
        await check_redis(),
        await check_s3(),
        check_email_config(),
        await check_migrations(),
        await check_cap(),
    ]
```

After `check_migrations_cmd`, add:

```python
@check_app.command(name="cap")
async def check_cap_cmd():
    """Check cap captcha server reachability."""
    if not await check_cap():
        sys.exit(1)
```

- [ ] **Step 6: Update the existing `test_check_email_config_valid` legacy test**

The pre-existing test in `tests/babycli/test_check.py`:

```python
def test_check_email_config_valid():
    env = {
        "EMAIL_SERVER": "smtp.example.com",
        "EMAIL_PORT": "587",
        "EMAIL_USERNAME": "user",
        "EMAIL_PASSWORD": "pass",
        "EMAIL_FROM_EMAIL": "noreply@example.com",
        "EMAIL_FROM_NAME": "Babytroc",
    }
    with patch.dict("os.environ", env, clear=True):
        result = check_email_config()
    assert result is True
```

now needs `CONTACT_EMAIL`. Replace with:

```python
def test_check_email_config_valid():
    env = {
        "EMAIL_SERVER": "smtp.example.com",
        "EMAIL_PORT": "587",
        "EMAIL_USERNAME": "user",
        "EMAIL_PASSWORD": "pass",
        "EMAIL_FROM_EMAIL": "noreply@example.com",
        "EMAIL_FROM_NAME": "Babytroc",
        "CONTACT_EMAIL": "contact@example.com",
    }
    with patch.dict("os.environ", env, clear=True):
        result = check_email_config()
    assert result is True
```

- [ ] **Step 7: Run tests to verify pass**

Run: `pytest tests/babycli/test_check.py -v`
Expected: PASS.

- [ ] **Step 8: Manual smoke of CLI command (optional but recommended)**

Run:

```bash
CAP_API_URL=http://localhost:1 CAP_SITE_KEY=x CAP_SECRET_KEY=y mise run babycli check cap
```

Expected: prints `Cap — <error>` and exits 1 (port 1 unreachable). Confirms CLI wiring.

- [ ] **Step 9: Commit**

```bash
git add src/babycli/check.py tests/babycli/test_check.py
git commit -m "feat(babycli): add 'check cap' and require CONTACT_EMAIL in check email"
```

---

## Task 11: Update CLAUDE.md env var list

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Find the env vars section in `CLAUDE.md`**

Section starts with: `### Environment` and lists required env vars.

- [ ] **Step 2: Add new vars to the required list**

Find the line:

```
Required env vars (see `src/babytroc/infrastructure/config.py`): `POSTGRES_{USER,PASSWORD,HOST,PORT,DATABASE}`, `EMAIL_{SERVER,PORT,USERNAME,PASSWORD,FROM_EMAIL,FROM_NAME}`, `S3_{ENDPOINT_URL,ACCESS_KEY,SECRET_KEY,BUCKET,PUBLIC_URL}`, `JWT_{ALGORITHM,SECRET_KEY,REFRESH_TOKEN_DURATION_DAYS,ACCESS_TOKEN_DURATION_MINUTES}`, `ACCOUNT_PASSWORD_RESET_AUTHORIZATION_DURATION_MINUTES`, `HOST_NAME`, `APP_NAME`. Optional: `DELAY` (artificial request delay middleware), `REDIS_{HOST,PORT,DB,PASSWORD}` (defaults: localhost, 6379, 0, none). `mise.toml` loads `.env.yaml` automatically.
```

Replace with:

```
Required env vars (see `src/babytroc/infrastructure/config.py`): `POSTGRES_{USER,PASSWORD,HOST,PORT,DATABASE}`, `EMAIL_{SERVER,PORT,USERNAME,PASSWORD,FROM_EMAIL,FROM_NAME}`, `S3_{ENDPOINT_URL,ACCESS_KEY,SECRET_KEY,BUCKET,PUBLIC_URL}`, `JWT_{ALGORITHM,SECRET_KEY,REFRESH_TOKEN_DURATION_DAYS,ACCESS_TOKEN_DURATION_MINUTES}`, `ACCOUNT_PASSWORD_RESET_AUTHORIZATION_DURATION_MINUTES`, `HOST_NAME`, `APP_NAME`, `CONTACT_EMAIL`, `CAP_{API_URL,SITE_KEY,SECRET_KEY}`. Optional: `DELAY` (artificial request delay middleware), `REDIS_{HOST,PORT,DB,PASSWORD}` (defaults: localhost, 6379, 0, none), `CONTACT_RATE_LIMIT_{ANON,AUTH}` (defaults 5, 10), `CONTACT_RATE_LIMIT_WINDOW_SECONDS` (default 3600). `mise.toml` loads `.env.yaml` automatically.
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: list contact and cap env vars in CLAUDE.md"
```

---

## Task 12: Final regression run

- [ ] **Step 1: Run the entire test suite**

Run: `mise run test`
Expected: PASS.

- [ ] **Step 2: Run full lint**

Run: `mise run lint`
Expected: PASS.

- [ ] **Step 3: Domain boundary check**

Run: `uv run babycli lint boundaries`
Expected: PASS — no new violations (the contact endpoint stays in `routers/`/`infrastructure/`, never crosses domains).

- [ ] **Step 4: Confirm working tree is clean**

Run: `git status`
Expected: working tree clean.

---

## Done

The endpoint `POST /api/v1/utils/contact` is implemented with:
- Pydantic validation (length, email)
- Honeypot field `website`
- Reusable `RateLimiter` (per-IP for anon, per-user for auth)
- External `cap` PoW captcha verification (fail-closed)
- HTML-escaped email body via fastapi-mail BackgroundTasks
- `Reply-To` set to submitter
- `babycli check cap` integrated
- Test coverage of every security layer

Spec satisfied. The `gui/app/pages/me/contact.vue` page now has a backend to call.
