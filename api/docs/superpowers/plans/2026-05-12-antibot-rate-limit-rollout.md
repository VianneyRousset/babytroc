# Anti-Bot + Rate Limit Rollout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the same honeypot + cap PoW + per-endpoint rate-limit pipeline that currently protects `POST /utils/contact` to four more public-mutation endpoints (signup, password-reset trigger, item create, image upload), via shared reusable building blocks; refactor the contact endpoint to consume the same shared bits.

**Architecture:** Two new reusable artifacts — `AntiBotMixin` + `verify_antibot()` in `shared/antibot.py`, and `make_rate_limit_dep()` factory in `shared/rate_limit.py`. A generic `RateLimitConfig` NamedTuple replaces ContactConfig's inline fields and serves four new top-level config fields. Each protected endpoint declares a router-local request schema composing the domain create schema with `AntiBotMixin`, calls `verify_antibot()` in the handler, and attaches a `make_rate_limit_dep`-built dependency. Domain services are unchanged.

**Tech Stack:** FastAPI, Pydantic v2 (NamedTuple configs, BaseModel schemas), Redis async client, pytest + pytest-asyncio (auto mode), httpx, monkeypatch.

**Reference:** Spec at `docs/superpowers/specs/2026-05-12-antibot-rate-limit-rollout-design.md`.

---

## Task 1: Add `RateLimitConfig` NamedTuple to infrastructure/config.py

**Files:**
- Modify: `src/babytroc/infrastructure/config.py` (add new class before `ContactConfig`)
- Test: `tests/test_config.py`

- [ ] **Step 1.1: Add the failing test**

Append to `tests/test_config.py` (create the file or append depending on whether it exists; the project already has `tests/test_config.py` — append a new test class).

```python
# tests/test_config.py — append at end

import os
from datetime import timedelta

import pytest

from babytroc.infrastructure.config import RateLimitConfig


class TestRateLimitConfig:
    def test_from_env_uses_defaults_when_unset(self, monkeypatch: pytest.MonkeyPatch):
        for k in ("SIGNUP_RATE_LIMIT_ANON", "SIGNUP_RATE_LIMIT_AUTH",
                  "SIGNUP_RATE_LIMIT_WINDOW_SECONDS",
                  "TEST_SIGNUP_RATE_LIMIT_ANON", "TEST_SIGNUP_RATE_LIMIT_AUTH",
                  "TEST_SIGNUP_RATE_LIMIT_WINDOW_SECONDS"):
            monkeypatch.delenv(k, raising=False)
        cfg = RateLimitConfig.from_env(
            env_prefix="SIGNUP",
            default_anon=3, default_auth=3, default_window_seconds=3600,
        )
        assert cfg.anon == 3
        assert cfg.auth == 3
        assert cfg.window == timedelta(seconds=3600)

    def test_from_env_reads_env_overrides(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("SIGNUP_RATE_LIMIT_ANON", "7")
        monkeypatch.setenv("SIGNUP_RATE_LIMIT_AUTH", "11")
        monkeypatch.setenv("SIGNUP_RATE_LIMIT_WINDOW_SECONDS", "120")
        cfg = RateLimitConfig.from_env(
            env_prefix="SIGNUP",
            default_anon=3, default_auth=3, default_window_seconds=3600,
        )
        assert cfg.anon == 7
        assert cfg.auth == 11
        assert cfg.window == timedelta(seconds=120)
```

Note: the project's `_env` helper prefers `TEST_` prefixed vars under `PYTEST_CURRENT_TEST`. The first test explicitly unsets both forms so defaults flow through. The override test sets the bare names because pytest will already have set `PYTEST_CURRENT_TEST`, and the project's convention in `tests/test_config.py` already monkeypatches the non-`TEST_` form — confirm by reading the existing test_config.py first; if it sets `TEST_*` instead, use the same prefix throughout.

- [ ] **Step 1.2: Verify the test fails**

Run: `pytest tests/test_config.py::TestRateLimitConfig -v`
Expected: FAIL with `ImportError: cannot import name 'RateLimitConfig' from 'babytroc.infrastructure.config'`.

- [ ] **Step 1.3: Implement `RateLimitConfig` in `infrastructure/config.py`**

Insert immediately above `class ContactConfig`:

```python
class RateLimitConfig(NamedTuple):
    anon: int
    auth: int
    window: timedelta

    @classmethod
    def from_env(
        cls,
        *,
        env_prefix: str,
        default_anon: int,
        default_auth: int,
        default_window_seconds: int,
    ) -> Self:
        anon = int(_env(f"{env_prefix}_RATE_LIMIT_ANON", default=str(default_anon)))
        auth = int(_env(f"{env_prefix}_RATE_LIMIT_AUTH", default=str(default_auth)))
        window = timedelta(
            seconds=int(
                _env(
                    f"{env_prefix}_RATE_LIMIT_WINDOW_SECONDS",
                    default=str(default_window_seconds),
                ),
            ),
        )
        return cls(anon=anon, auth=auth, window=window)
```

- [ ] **Step 1.4: Verify the test passes**

Run: `pytest tests/test_config.py::TestRateLimitConfig -v`
Expected: PASS (2 tests).

- [ ] **Step 1.5: Commit**

```bash
git add src/babytroc/infrastructure/config.py tests/test_config.py
git commit -m "feat(config): add generic RateLimitConfig NamedTuple"
```

---

## Task 2: Refactor `ContactConfig` to nest `RateLimitConfig`

**Files:**
- Modify: `src/babytroc/infrastructure/config.py` (replace `ContactConfig`)
- Modify: `tests/test_config.py` (existing tests for ContactConfig need shape update)
- Modify: `src/babytroc/routers/v1/utils/contact.py` (callers reading `config.contact.rate_limit_anon` etc.)
- Modify: `src/babycli/check.py` (if it reads contact rate-limit fields directly — verify first)

- [ ] **Step 2.1: Find all callers of `config.contact.rate_limit_*`**

Run: `grep -rn "contact\.rate_limit_anon\|contact\.rate_limit_auth\|contact\.rate_limit_window" src tests`
Note each call site. Expected hits: `src/babytroc/routers/v1/utils/contact.py` (in `rate_limit_contact`); possibly tests.

- [ ] **Step 2.2: Update the failing test for ContactConfig shape**

Update tests in `tests/test_config.py` that assert on `ContactConfig.rate_limit_anon` etc. New expected shape:

```python
def test_contact_config_nests_rate_limit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CONTACT_EMAIL", "ops@example.com")
    monkeypatch.setenv("CONTACT_RATE_LIMIT_ANON", "5")
    monkeypatch.setenv("CONTACT_RATE_LIMIT_AUTH", "10")
    monkeypatch.setenv("CONTACT_RATE_LIMIT_WINDOW_SECONDS", "3600")
    cfg = ContactConfig.from_env()
    assert cfg.email == "ops@example.com"
    assert cfg.rate_limit.anon == 5
    assert cfg.rate_limit.auth == 10
    assert cfg.rate_limit.window == timedelta(seconds=3600)
```

Replace any prior test asserting `cfg.rate_limit_anon` etc. with assertions on `cfg.rate_limit.anon`.

- [ ] **Step 2.3: Run the updated test (expect failure)**

Run: `pytest tests/test_config.py::test_contact_config_nests_rate_limit -v`
Expected: FAIL with `AttributeError: 'ContactConfig' object has no attribute 'rate_limit'`.

- [ ] **Step 2.4: Replace `ContactConfig` in `infrastructure/config.py`**

Replace the entire `class ContactConfig` block with:

```python
class ContactConfig(NamedTuple):
    email: str
    rate_limit: RateLimitConfig

    @classmethod
    def from_env(
        cls,
        email: str | None = None,
        rate_limit: RateLimitConfig | None = None,
    ) -> Self:
        if email is None:
            email = _env("CONTACT_EMAIL")
        if rate_limit is None:
            rate_limit = RateLimitConfig.from_env(
                env_prefix="CONTACT",
                default_anon=5,
                default_auth=10,
                default_window_seconds=3600,
            )
        return cls(email=email, rate_limit=rate_limit)
```

- [ ] **Step 2.5: Update `rate_limit_contact` in `routers/v1/utils/contact.py`**

Replace the body of `rate_limit_contact`'s limiter construction so it reads from `config.contact.rate_limit`:

```python
# in routers/v1/utils/contact.py — patch only the limiter build site
limiter = RateLimiter(
    key_prefix="contact",
    anon_limit=config.contact.rate_limit.anon,
    auth_limit=config.contact.rate_limit.auth,
    window=config.contact.rate_limit.window,
)
```

(Full replacement of this file happens later in Task 7; for now do a minimal in-place fix so existing tests keep passing.)

- [ ] **Step 2.6: Update any other call sites identified in Step 2.1**

If `src/babycli/check.py` reads `config.contact.rate_limit_*`, update to `config.contact.rate_limit.*`. Same for any tests still on the old shape.

- [ ] **Step 2.7: Run all config + contact tests**

Run: `pytest tests/test_config.py tests/utils/test_contact.py -v`
Expected: PASS.

- [ ] **Step 2.8: Commit**

```bash
git add src/babytroc/infrastructure/config.py src/babytroc/routers/v1/utils/contact.py tests/test_config.py
git commit -m "refactor(config): nest RateLimitConfig inside ContactConfig"
```

---

## Task 3: Add four new top-level rate-limit configs

**Files:**
- Modify: `src/babytroc/infrastructure/config.py` (extend `Config`)
- Modify: `tests/test_config.py`

- [ ] **Step 3.1: Add failing test for the new Config fields**

Append to `tests/test_config.py`:

```python
class TestConfigRateLimits:
    def test_config_has_signup_password_reset_item_create_image_upload(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ):
        # Defaults: signup 3, password_reset 3, item_create 30, image_upload 60.
        # Ensure overrides aren't bleeding in from the env.
        for prefix in ("SIGNUP", "PASSWORD_RESET", "ITEM_CREATE", "IMAGE_UPLOAD"):
            for suffix in ("ANON", "AUTH", "WINDOW_SECONDS"):
                monkeypatch.delenv(f"{prefix}_RATE_LIMIT_{suffix}", raising=False)
                monkeypatch.delenv(f"TEST_{prefix}_RATE_LIMIT_{suffix}", raising=False)
        cfg = Config.from_env()
        assert cfg.signup.anon == 3
        assert cfg.signup.auth == 3
        assert cfg.password_reset.anon == 3
        assert cfg.item_create.anon == 30
        assert cfg.item_create.auth == 30
        assert cfg.image_upload.anon == 60
        assert cfg.image_upload.auth == 60
```

The test relies on `Config.from_env()` working in the test environment, which it does today (see `tests/test_config.py` for the existing pattern).

- [ ] **Step 3.2: Verify it fails**

Run: `pytest tests/test_config.py::TestConfigRateLimits -v`
Expected: FAIL with `AttributeError: 'Config' object has no attribute 'signup'`.

- [ ] **Step 3.3: Add fields to `Config`**

Extend the `class Config(NamedTuple)` declaration to add four fields after `cap`:

```python
class Config(NamedTuple):
    host_name: str
    app_name: str
    root_path: str
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
    signup: RateLimitConfig
    password_reset: RateLimitConfig
    item_create: RateLimitConfig
    image_upload: RateLimitConfig
```

Extend `Config.from_env` to accept and build each one. Add four parameters (after `cap`) and four blocks (after the `cap` build block):

```python
        signup: RateLimitConfig | None = None,
        password_reset: RateLimitConfig | None = None,
        item_create: RateLimitConfig | None = None,
        image_upload: RateLimitConfig | None = None,
```

```python
        if signup is None:
            signup = RateLimitConfig.from_env(
                env_prefix="SIGNUP",
                default_anon=3, default_auth=3, default_window_seconds=3600,
            )
        if password_reset is None:
            password_reset = RateLimitConfig.from_env(
                env_prefix="PASSWORD_RESET",
                default_anon=3, default_auth=3, default_window_seconds=3600,
            )
        if item_create is None:
            item_create = RateLimitConfig.from_env(
                env_prefix="ITEM_CREATE",
                default_anon=30, default_auth=30, default_window_seconds=3600,
            )
        if image_upload is None:
            image_upload = RateLimitConfig.from_env(
                env_prefix="IMAGE_UPLOAD",
                default_anon=60, default_auth=60, default_window_seconds=3600,
            )
```

And extend the `return cls(...)` block to include all four new fields.

- [ ] **Step 3.4: Verify the test passes**

Run: `pytest tests/test_config.py::TestConfigRateLimits -v`
Expected: PASS.

- [ ] **Step 3.5: Commit**

```bash
git add src/babytroc/infrastructure/config.py tests/test_config.py
git commit -m "feat(config): add signup/password_reset/item_create/image_upload rate-limit configs"
```

---

## Task 4: Create `shared/antibot.py` with `AntiBotMixin` + `verify_antibot`

**Files:**
- Create: `src/babytroc/shared/antibot.py`
- Test: `tests/shared/test_antibot.py`

- [ ] **Step 4.1: Write the failing tests**

Create `tests/shared/test_antibot.py`:

```python
import pytest

from babytroc.infrastructure.config import CapConfig
from babytroc.shared.antibot import AntiBotMixin, verify_antibot
from babytroc.shared.errors import BadRequestError


CAP_CONFIG = CapConfig(
    api_url="https://cap.example.com",
    site_key="site",
    secret_key="secret",
)


class _Payload(AntiBotMixin):
    """Composing schema used only to instantiate the mixin in tests."""


def _payload(*, cap_token: str = "valid", website: str = "") -> _Payload:
    return _Payload(cap_token=cap_token, website=website)


# --- mixin validation ---

def test_mixin_requires_cap_token():
    with pytest.raises(Exception):  # pydantic ValidationError
        _Payload(website="")  # type: ignore[call-arg]


def test_mixin_website_defaults_to_empty():
    p = _Payload(cap_token="t")
    assert p.website == ""


def test_mixin_rejects_cap_token_too_long():
    with pytest.raises(Exception):
        _Payload(cap_token="x" * 4097)


# --- verify_antibot ---

async def test_verify_antibot_passes_when_clean(monkeypatch: pytest.MonkeyPatch):
    async def _ok(_config, _token):
        return True
    monkeypatch.setattr("babytroc.shared.antibot.verify_cap_token", _ok)
    await verify_antibot(_payload(), CAP_CONFIG)  # should not raise


async def test_verify_antibot_rejects_filled_honeypot():
    with pytest.raises(BadRequestError) as exc:
        await verify_antibot(_payload(website="x"), CAP_CONFIG)
    assert exc.value.message == "INVALID_SUBMISSION"


async def test_verify_antibot_rejects_when_cap_fails(monkeypatch: pytest.MonkeyPatch):
    async def _fail(_config, _token):
        return False
    monkeypatch.setattr("babytroc.shared.antibot.verify_cap_token", _fail)
    with pytest.raises(BadRequestError) as exc:
        await verify_antibot(_payload(), CAP_CONFIG)
    assert exc.value.message == "INVALID_SUBMISSION"


async def test_verify_antibot_runs_honeypot_before_cap(monkeypatch: pytest.MonkeyPatch):
    cap_called = False
    async def _spy(_config, _token):
        nonlocal cap_called
        cap_called = True
        return True
    monkeypatch.setattr("babytroc.shared.antibot.verify_cap_token", _spy)
    with pytest.raises(BadRequestError):
        await verify_antibot(_payload(website="x"), CAP_CONFIG)
    assert cap_called is False
```

- [ ] **Step 4.2: Verify the tests fail**

Run: `pytest tests/shared/test_antibot.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'babytroc.shared.antibot'`.

- [ ] **Step 4.3: Implement `shared/antibot.py`**

Create `src/babytroc/shared/antibot.py`:

```python
from typing import Annotated

from pydantic import BaseModel, StringConstraints

from babytroc.infrastructure.cap import verify_cap_token
from babytroc.infrastructure.config import CapConfig
from babytroc.shared.errors import BadRequestError


class AntiBotMixin(BaseModel):
    """Mixin contributing transport-only anti-bot fields.

    Compose into router-layer request schemas; never inherit into domain
    schemas — services must not require cap_token/website.
    """

    cap_token: Annotated[str, StringConstraints(min_length=1, max_length=4096)]
    website: str = ""  # honeypot — bots fill, humans don't see


async def verify_antibot(payload: AntiBotMixin, cap_config: CapConfig) -> None:
    """Run honeypot then cap PoW check. Raise BadRequestError on either failure.

    Both rejections surface as the same shared 400 INVALID_SUBMISSION error
    so the response cannot be used as a probe oracle for which layer fired.
    """
    if payload.website:
        msg = "INVALID_SUBMISSION"
        raise BadRequestError(msg)
    if not await verify_cap_token(cap_config, payload.cap_token):
        msg = "INVALID_SUBMISSION"
        raise BadRequestError(msg)
```

- [ ] **Step 4.4: Verify the tests pass**

Run: `pytest tests/shared/test_antibot.py -v`
Expected: PASS (6 tests).

- [ ] **Step 4.5: Commit**

```bash
git add src/babytroc/shared/antibot.py tests/shared/test_antibot.py
git commit -m "feat(shared): add AntiBotMixin and verify_antibot helper"
```

---

## Task 5: Add `make_rate_limit_dep` factory to `shared/rate_limit.py`

**Files:**
- Modify: `src/babytroc/shared/rate_limit.py`
- Test: `tests/shared/test_rate_limit.py`

- [ ] **Step 5.1: Write the failing test**

Append to `tests/shared/test_rate_limit.py`:

```python
class TestMakeRateLimitDep:
    async def test_factory_builds_dep_and_caches_limiter_on_app_state(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ):
        from datetime import timedelta
        from unittest.mock import AsyncMock, MagicMock

        from babytroc.shared.rate_limit import make_rate_limit_dep
        from babytroc.infrastructure.config import RateLimitConfig

        rl_config = RateLimitConfig(
            anon=2, auth=5, window=timedelta(seconds=60),
        )
        app_state = MagicMock()
        # Strip any pre-existing cache attribute so we know the dep builds one.
        for attr in list(vars(app_state)):
            if attr.startswith("_rate_limiter_"):
                delattr(app_state, attr)
        app_state.config = MagicMock()
        app_state.config.signup = rl_config

        scope = {
            "type": "http", "method": "POST", "path": "/",
            "headers": [], "client": ("1.2.3.4", 12345),
            "app": MagicMock(state=app_state),
        }
        request = Request(scope=scope)
        redis = AsyncMock()
        redis.incr = AsyncMock(return_value=1)
        redis.expire = AsyncMock()

        dep = make_rate_limit_dep(
            key_prefix="signup",
            extract_config=lambda c: c.signup,
        )
        await dep(request=request, redis=redis, client_id=None)

        # limiter was built and cached
        assert hasattr(app_state, "_rate_limiter_signup")
        # second call reuses the cached limiter
        await dep(request=request, redis=redis, client_id=None)
        # incr was called twice (once per request)
        assert redis.incr.await_count == 2
```

The existing `_make_request` helper at the top of the file does not set `app.state.config`; this test builds its own scope.

- [ ] **Step 5.2: Verify the test fails**

Run: `pytest tests/shared/test_rate_limit.py::TestMakeRateLimitDep -v`
Expected: FAIL with `ImportError: cannot import name 'make_rate_limit_dep'`.

- [ ] **Step 5.3: Add `make_rate_limit_dep` to `shared/rate_limit.py`**

Append to `src/babytroc/shared/rate_limit.py`:

```python
from collections.abc import Awaitable, Callable

from babytroc.infrastructure.config import Config, RateLimitConfig


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
```

If `Config` and `RateLimitConfig` import would create a cycle (it would not, since config doesn't import shared), put the imports at the top of the file with the others. Verify import order with the existing imports.

- [ ] **Step 5.4: Verify the test passes**

Run: `pytest tests/shared/test_rate_limit.py -v`
Expected: PASS (existing tests + new one).

- [ ] **Step 5.5: Commit**

```bash
git add src/babytroc/shared/rate_limit.py tests/shared/test_rate_limit.py
git commit -m "feat(shared): add make_rate_limit_dep factory for per-endpoint limiters"
```

---

## Task 6: Migrate `tests/fixtures/contact.py` → `tests/fixtures/antibot.py`

**Files:**
- Create: `tests/fixtures/antibot.py`
- Delete: `tests/fixtures/contact.py`
- Modify: `tests/conftest.py` (update `pytest_plugins`)

- [ ] **Step 6.1: Create the new shared fixture file**

Create `tests/fixtures/antibot.py`:

```python
from collections.abc import AsyncGenerator, Callable
from datetime import timedelta
from typing import Any

import pytest
from fastapi import FastAPI

from babytroc.infrastructure import cap as cap_module
from babytroc.shared import antibot as antibot_module
from babytroc.shared.rate_limit import RateLimiter


@pytest.fixture
def cap_verify_result() -> bool:
    """Override via `@pytest.mark.parametrize` to make the stub return False."""
    return True


@pytest.fixture(autouse=True)
def stub_cap_verify(
    monkeypatch: pytest.MonkeyPatch,
    cap_verify_result: bool,
):
    """Replace `verify_cap_token` so tests don't reach a real cap server.

    `shared/antibot.py` imports `verify_cap_token` from
    `babytroc.infrastructure.cap`, so we patch the symbol on the module the
    helper imported it from. We also patch the source module for completeness.
    """

    async def _fake(_config, _token):
        return cap_verify_result

    monkeypatch.setattr(cap_module, "verify_cap_token", _fake)
    monkeypatch.setattr(antibot_module, "verify_cap_token", _fake)


@pytest.fixture
def tight_rate_limit_factory(app: FastAPI) -> Callable[..., Any]:
    """Return a function that overrides one endpoint's rate-limit dep with
    tight values so rate-limit tests run fast.

    Usage:
        tight_rate_limit_factory(
            dep=rate_limit_signup,
            key_prefix="signup-test",
            anon_limit=2, auth_limit=3, window_seconds=60,
        )
    """

    def _set(
        *,
        dep: Callable[..., Any],
        key_prefix: str,
        anon_limit: int,
        auth_limit: int,
        window_seconds: int,
    ) -> None:
        new = RateLimiter(
            key_prefix=key_prefix,
            anon_limit=anon_limit,
            auth_limit=auth_limit,
            window=timedelta(seconds=window_seconds),
        )
        app.dependency_overrides[dep] = new

    return _set


@pytest.fixture(autouse=True)
async def _clear_rate_limit_overrides(app: FastAPI) -> AsyncGenerator[None]:
    """Clear any dep overrides set during the test, plus any cached limiter
    instances stashed on `app.state` (so default-limit tests start fresh)."""
    yield
    app.dependency_overrides.clear()
    for attr in [a for a in vars(app.state) if a.startswith("_rate_limiter_")]:
        delattr(app.state, attr)
```

Note: `app.dependency_overrides.clear()` is acceptable here because each test should declare any deps it relies on (the project doesn't appear to set global overrides). Verify with: `grep -rn "app.dependency_overrides\[" tests/` — if any other fixture pre-populates the overrides, change `.clear()` to pop only the specific deps we set.

- [ ] **Step 6.2: Delete the old contact fixture file**

```bash
git rm tests/fixtures/contact.py
```

- [ ] **Step 6.3: Update `tests/conftest.py::pytest_plugins`**

Replace the line `"tests.fixtures.contact",` with `"tests.fixtures.antibot",`.

- [ ] **Step 6.4: Update `tests/utils/test_contact.py` to use the new fixture API**

The old contact fixture had a different `tight_rate_limit_factory` signature (no `dep` argument). Find usages in `tests/utils/test_contact.py`:

Run: `grep -n "tight_rate_limit_factory" tests/utils/test_contact.py`

For each call, update to pass the `dep` explicitly:

```python
from babytroc.routers.v1.utils.contact import rate_limit_contact

tight_rate_limit_factory(
    dep=rate_limit_contact,
    key_prefix="contact-test",
    anon_limit=2, auth_limit=3, window_seconds=60,
)
```

- [ ] **Step 6.5: Run the full test suite to check fixture migration**

Run: `pytest tests/utils/test_contact.py tests/shared/ -v`
Expected: PASS.

- [ ] **Step 6.6: Commit**

```bash
git add tests/fixtures/antibot.py tests/conftest.py tests/utils/test_contact.py
git commit -m "test: rename contact fixtures to antibot, generalize for reuse"
```

---

## Task 7: Refactor `routers/v1/utils/contact.py` to use shared antibot + factory

**Files:**
- Modify: `src/babytroc/routers/v1/utils/contact.py`
- Test: `tests/utils/test_contact.py` (should pass unchanged after Task 6)

- [ ] **Step 7.1: Rewrite the contact router file**

Replace the entire content of `src/babytroc/routers/v1/utils/contact.py` with:

```python
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Request, status
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr, StringConstraints

from babytroc.infrastructure.email import get_email_client
from babytroc.infrastructure.email_contact import send_contact_email
from babytroc.routers.v1.auth.verification import maybe_verify_request_credentials
from babytroc.shared.antibot import AntiBotMixin, verify_antibot
from babytroc.shared.rate_limit import make_rate_limit_dep

if TYPE_CHECKING:
    from babytroc.infrastructure.config import Config

router = APIRouter()


class ContactSubmit(AntiBotMixin, BaseModel):
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


rate_limit_contact = make_rate_limit_dep(
    key_prefix="contact",
    extract_config=lambda c: c.contact.rate_limit,
)


@router.post("/contact", status_code=status.HTTP_204_NO_CONTENT)
async def submit_contact(
    payload: Annotated[ContactSubmit, Body()],
    request: Request,
    background_tasks: BackgroundTasks,
    _rate_limited: Annotated[None, Depends(rate_limit_contact)],
    client_id: Annotated[int | None, Depends(maybe_verify_request_credentials)],
) -> Response:
    config: Config = request.app.state.config
    await verify_antibot(payload, config.cap)

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

This drops the inline `rate_limit_contact` lazy-build, the inline honeypot+cap inline checks, and the inline `cap_token`/`website` fields — all replaced by shared bits.

- [ ] **Step 7.2: Verify contact tests still pass**

Run: `pytest tests/utils/test_contact.py -v`
Expected: PASS (all existing tests).

If any test fails because of the rate-limit-before-honeypot order (the spec moves rate-limit to step 2), update the affected test. Specifically: if there's a test that asserts honeypot rejection happens before rate-limit rejection in a single request, that assumption no longer holds; rate-limit gates first now. Honeypot-only tests (request that passes rate-limit) and rate-limit-only tests (request without filled honeypot) still work independently — only a test that combined both layers in the same request would need updating.

- [ ] **Step 7.3: Commit**

```bash
git add src/babytroc/routers/v1/utils/contact.py
git commit -m "refactor(contact): consume shared AntiBotMixin + make_rate_limit_dep"
```

---

## Task 8: Add antibot + rate-limit to `POST /api/v1/auth/new` (signup)

**Files:**
- Modify: `src/babytroc/routers/v1/auth/new.py`
- Modify: `tests/test_auth.py` (existing test signs up — needs `cap_token`)
- Create: `tests/auth/__init__.py` (if it doesn't exist)
- Create: `tests/auth/test_signup_antibot.py`

- [ ] **Step 8.1: Inspect existing signup test, add cap_token to its payload**

Run: `grep -n '"/api/v1/auth/new"' tests/test_auth.py`. For each POST to that endpoint in tests, append `"cap_token": "valid"` (any non-empty string) and ensure no `"website"` is set. The autouse `stub_cap_verify` fixture in `tests/fixtures/antibot.py` makes cap return True.

Example edit (lines around 144 and 263 per current state of test_auth.py):

```python
resp = await client.post(
    "/api/v1/auth/new",
    json={
        "name": "newaccount",
        "email": email,
        "password": password,
        "cap_token": "valid",
    },
)
```

- [ ] **Step 8.2: Run the existing test to confirm it currently passes (before our endpoint change)**

Run: `pytest tests/test_auth.py -v -k "test_create_account" --co` first to find the test name, then run it. Adjust the `-k` filter to match the actual test name in the file.

If the test passes after only the payload update (still no endpoint change), it means pydantic accepts extra fields. Either way, proceed.

- [ ] **Step 8.3: Write failing antibot tests**

Ensure `tests/auth/__init__.py` exists; create it empty if not.

Create `tests/auth/test_signup_antibot.py`:

```python
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.user.models import User
from babytroc.routers.v1.auth.new import rate_limit_signup

VALID = {
    "name": "newperson",
    "email": "newperson@example.com",
    "password": "Pa55word42",
    "cap_token": "valid",
}


def _payload(**overrides) -> dict:
    return {**VALID, **overrides}


async def _count_users(database_sessionmaker: async_sessionmaker) -> int:
    async with database_sessionmaker() as db:
        result = await db.execute(select(User))
        return len(result.scalars().all())


async def test_happy_path_creates_user(
    client: AsyncClient,
    database_sessionmaker: async_sessionmaker,
):
    before = await _count_users(database_sessionmaker)
    resp = await client.post("/api/v1/auth/new", json=_payload())
    assert resp.status_code == 200
    after = await _count_users(database_sessionmaker)
    assert after == before + 1


async def test_honeypot_rejects_with_400_invalid_submission(
    client: AsyncClient,
    database_sessionmaker: async_sessionmaker,
):
    before = await _count_users(database_sessionmaker)
    resp = await client.post(
        "/api/v1/auth/new", json=_payload(website="bot was here"),
    )
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"
    after = await _count_users(database_sessionmaker)
    assert after == before


@pytest.mark.parametrize("cap_verify_result", [False])
async def test_cap_rejected_returns_400_invalid_submission(
    client: AsyncClient,
    database_sessionmaker: async_sessionmaker,
    cap_verify_result: bool,
):
    before = await _count_users(database_sessionmaker)
    resp = await client.post("/api/v1/auth/new", json=_payload())
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"
    after = await _count_users(database_sessionmaker)
    assert after == before


async def test_rate_limit_anon_returns_429(
    client: AsyncClient,
    tight_rate_limit_factory,
):
    tight_rate_limit_factory(
        dep=rate_limit_signup,
        key_prefix="signup-test",
        anon_limit=2, auth_limit=2, window_seconds=60,
    )
    # 2 hits OK
    r1 = await client.post("/api/v1/auth/new", json=_payload(email="a@a.com"))
    r2 = await client.post("/api/v1/auth/new", json=_payload(email="b@b.com"))
    assert r1.status_code == 200
    assert r2.status_code == 200
    # 3rd hit rate-limited
    r3 = await client.post("/api/v1/auth/new", json=_payload(email="c@c.com"))
    assert r3.status_code == 429
```

Adjust the expected 200 status code to whatever the current signup endpoint returns (the existing handler returns `UserCredentialsInfo`, default FastAPI status 200). If it returns 201, change the assertions.

- [ ] **Step 8.4: Run the new tests to confirm they fail before the change**

Run: `pytest tests/auth/test_signup_antibot.py -v`
Expected: FAIL — likely `ImportError: cannot import name 'rate_limit_signup'` from the route module, since we haven't added it yet.

- [ ] **Step 8.5: Modify `routers/v1/auth/new.py`**

Replace the file content with:

```python
from typing import TYPE_CHECKING, Annotated

from fastapi import BackgroundTasks, Depends, Request, Response
from fastapi_mail import FastMail
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.auth import services as auth_services
from babytroc.domains.auth.schemas.credentials import UserCredentialsInfo
from babytroc.domains.user import services as user_services
from babytroc.domains.user.schemas.create import UserCreate
from babytroc.infrastructure.database import get_db_session
from babytroc.infrastructure.email import get_email_client
from babytroc.shared.antibot import AntiBotMixin, verify_antibot
from babytroc.shared.rate_limit import make_rate_limit_dep

from .cookies import set_response_with_token_cookies
from .router import router

if TYPE_CHECKING:
    from babytroc.infrastructure.config import Config


class UserCreateRequest(AntiBotMixin, UserCreate):
    pass


rate_limit_signup = make_rate_limit_dep(
    key_prefix="signup",
    extract_config=lambda c: c.signup,
)


@router.post("/new")
async def create_user(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    email_client: Annotated[FastMail, Depends(get_email_client)],
    background_tasks: BackgroundTasks,
    user_create_request: UserCreateRequest,
    request: Request,
    response: Response,
    _rate_limited: Annotated[None, Depends(rate_limit_signup)],
) -> UserCredentialsInfo:
    """Create a new user."""

    config: Config = request.app.state.config
    await verify_antibot(user_create_request, config.cap)

    user_create = UserCreate.model_validate(
        user_create_request.model_dump(exclude={"cap_token", "website"}),
    )

    await user_services.create_user(
        db=db,
        email_client=email_client,
        host_name=config.host_name,
        app_name=config.app_name,
        background_tasks=background_tasks,
        user_create=user_create,
    )

    credentials = await auth_services.login_user(
        db=db,
        email=user_create.email,
        password=user_create.password,
        config=config.auth,
    )

    set_response_with_token_cookies(
        response=response,
        request=request,
        credentials=credentials,
    )

    return UserCredentialsInfo(
        expires_in=round(credentials.access_token_duration.total_seconds()),
        validated=credentials.validated,
    )
```

- [ ] **Step 8.6: Run the antibot tests**

Run: `pytest tests/auth/test_signup_antibot.py -v`
Expected: PASS (4 tests).

- [ ] **Step 8.7: Run existing auth tests**

Run: `pytest tests/test_auth.py -v`
Expected: PASS (after the cap_token payload patch from Step 8.1).

- [ ] **Step 8.8: Commit**

```bash
git add src/babytroc/routers/v1/auth/new.py tests/test_auth.py tests/auth/test_signup_antibot.py
git commit -m "feat(auth): add antibot + rate-limit to signup endpoint"
```

If `tests/auth/__init__.py` was created, include it in the same commit.

---

## Task 9: Add antibot + rate-limit to `POST /api/v1/auth/reset-password` (trigger only)

**Files:**
- Modify: `src/babytroc/routers/v1/auth/reset.py`
- Modify: `tests/test_auth.py` (existing reset trigger tests need `cap_token`)
- Create: `tests/auth/test_reset_antibot.py`

- [ ] **Step 9.1: Patch existing test payloads**

Run: `grep -n '"/api/v1/auth/reset-password"' tests/test_auth.py` (no trailing `/{authorization_code}`).

For each call **to the trigger endpoint** (no `/{authorization_code}` suffix), append `"cap_token": "valid"` to the JSON payload. Example:

```python
resp = await client.post(
    "/api/v1/auth/reset-password",
    json={"email": alice_user_data["email"], "cap_token": "valid"},
)
```

Leave the apply step (`/api/v1/auth/reset-password/{code}`) alone.

- [ ] **Step 9.2: Write failing antibot tests**

Create `tests/auth/test_reset_antibot.py`:

```python
import pytest
from httpx import AsyncClient

from babytroc.routers.v1.auth.reset import rate_limit_password_reset


def _payload(*, email: str = "alice@example.com", **overrides) -> dict:
    return {"email": email, "cap_token": "valid", **overrides}


async def test_happy_path_returns_success(client: AsyncClient, alice):
    resp = await client.post(
        "/api/v1/auth/reset-password", json=_payload(email=alice.email),
    )
    assert resp.is_success


async def test_honeypot_returns_400_invalid_submission(
    client: AsyncClient, alice,
):
    resp = await client.post(
        "/api/v1/auth/reset-password",
        json=_payload(email=alice.email, website="x"),
    )
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"


@pytest.mark.parametrize("cap_verify_result", [False])
async def test_cap_rejected_returns_400(
    client: AsyncClient, alice, cap_verify_result: bool,
):
    resp = await client.post(
        "/api/v1/auth/reset-password", json=_payload(email=alice.email),
    )
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"


async def test_rate_limit_anon_returns_429(
    client: AsyncClient, alice, tight_rate_limit_factory,
):
    tight_rate_limit_factory(
        dep=rate_limit_password_reset,
        key_prefix="password-reset-test",
        anon_limit=1, auth_limit=1, window_seconds=60,
    )
    r1 = await client.post(
        "/api/v1/auth/reset-password", json=_payload(email=alice.email),
    )
    assert r1.is_success
    r2 = await client.post(
        "/api/v1/auth/reset-password", json=_payload(email=alice.email),
    )
    assert r2.status_code == 429
```

- [ ] **Step 9.3: Verify these fail**

Run: `pytest tests/auth/test_reset_antibot.py -v`
Expected: FAIL (`ImportError: rate_limit_password_reset`).

- [ ] **Step 9.4: Modify `routers/v1/auth/reset.py`**

Replace the trigger endpoint (only the `POST /reset-password` handler, not the apply endpoint) and add the request schema:

```python
from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from fastapi import BackgroundTasks, Depends, Request
from fastapi_mail import FastMail
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.auth import services as auth_services
from babytroc.domains.auth.schemas.create import AuthAccountPasswordResetAuthorizationCreate
from babytroc.domains.auth.schemas.reset import (
    AuthAccountPasswordResetAuthorizationCreated,
    AuthAccountPasswordResetDone,
)
from babytroc.domains.user.schemas.update import UserPasswordUpdate
from babytroc.infrastructure.database import get_db_session
from babytroc.infrastructure.email import get_email_client
from babytroc.shared.antibot import AntiBotMixin, verify_antibot
from babytroc.shared.rate_limit import make_rate_limit_dep

from .router import router

if TYPE_CHECKING:
    from babytroc.infrastructure.config import Config


class PasswordResetRequest(AntiBotMixin, AuthAccountPasswordResetAuthorizationCreate):
    pass


rate_limit_password_reset = make_rate_limit_dep(
    key_prefix="password_reset",
    extract_config=lambda c: c.password_reset,
)


@router.post("/reset-password")
async def create_account_password_reset_authorization(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    email_client: Annotated[FastMail, Depends(get_email_client)],
    background_tasks: BackgroundTasks,
    reset_request: PasswordResetRequest,
    _rate_limited: Annotated[None, Depends(rate_limit_password_reset)],
) -> AuthAccountPasswordResetAuthorizationCreated:
    """Send an account password reset authorization by email."""

    config: Config = request.app.state.config
    await verify_antibot(reset_request, config.cap)

    await auth_services.create_account_password_reset_authrorization(
        db=db,
        user_email=reset_request.email,
        email_client=email_client,
        background_tasks=background_tasks,
        host_name=config.host_name,
        app_name=config.app_name,
    )

    return AuthAccountPasswordResetAuthorizationCreated()


@router.post("/reset-password/{authorization_code}")
async def apply_account_password_reset(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    email_client: Annotated[FastMail, Depends(get_email_client)],
    background_tasks: BackgroundTasks,
    authorization_code: UUID,
    user_password_update: UserPasswordUpdate,
) -> AuthAccountPasswordResetDone:
    """Apply the account password reset with `authorization_code`."""

    await auth_services.apply_account_password_reset(
        db=db,
        authorization_code=authorization_code,
        new_password=user_password_update.password,
        email_client=email_client,
        background_tasks=background_tasks,
        app_name=request.app.state.config.app_name,
        config=request.app.state.config.auth,
    )

    return AuthAccountPasswordResetDone()
```

- [ ] **Step 9.5: Run the new tests**

Run: `pytest tests/auth/test_reset_antibot.py -v`
Expected: PASS.

- [ ] **Step 9.6: Run the existing auth tests**

Run: `pytest tests/test_auth.py -v`
Expected: PASS.

- [ ] **Step 9.7: Commit**

```bash
git add src/babytroc/routers/v1/auth/reset.py tests/test_auth.py tests/auth/test_reset_antibot.py
git commit -m "feat(auth): add antibot + rate-limit to password-reset trigger"
```

---

## Task 10: Add antibot + rate-limit to `POST /api/v1/me/items`

**Files:**
- Modify: `src/babytroc/routers/v1/me/items/create.py`
- Modify: `tests/fixtures/items.py` (the `alice_new_item_data` fixture must include `cap_token`)
- Modify: `tests/item/test_item_create.py`, `tests/item/test_item_categories.py`, `tests/item/test_item_images.py`, `tests/item/test_item_update.py` — any test that does `POST /api/v1/me/items`

- [ ] **Step 10.1: Find every POST to `/api/v1/me/items`**

Run: `grep -rn '"/api/v1/me/items"\|/api/v1/me/items' tests/ src/`. Note each POST call site in tests.

- [ ] **Step 10.2: Add `cap_token` to the `alice_new_item_data` (and equivalent) fixtures**

If item-create test payloads come from a fixture (likely `tests/fixtures/items.py::alice_new_item_data` etc.), append `"cap_token": "valid"` to the returned dict:

```python
return {
    "name": "new-item",
    "description": "This is the latest new item created by alice.",
    "targeted_age_months": "7-",
    "regions": [regions[1].id],
    "images": [image.name for image in alice_new_item_images],
    "cap_token": "valid",
}
```

Repeat for every test-item-creation fixture (`alice_new_item_data`, `alice_special_item_data`, any other `new_item_data` variants used in POST flows). Leave fixtures that represent existing item data (already-stored items, not POST bodies) untouched — those are dicts the test uses for assertions, not request bodies.

If tests use an inline `json={...}` dict for item creation in addition to fixtures, update those too.

- [ ] **Step 10.3: Write failing antibot tests**

Ensure `tests/item/__init__.py` exists. Create `tests/item/test_item_create_antibot.py`:

```python
import pytest
from httpx import AsyncClient

from babytroc.routers.v1.me.items.create import rate_limit_item_create
from tests.fixtures.items import ItemData


async def test_happy_path_creates_item(
    alice_client: AsyncClient,
    alice_new_item_data: ItemData,
):
    resp = await alice_client.post(
        "/api/v1/me/items", json=alice_new_item_data,
    )
    assert resp.status_code == 201


async def test_honeypot_rejects_with_400(
    alice_client: AsyncClient,
    alice_new_item_data: ItemData,
):
    body = {**alice_new_item_data, "website": "x"}
    resp = await alice_client.post("/api/v1/me/items", json=body)
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"


@pytest.mark.parametrize("cap_verify_result", [False])
async def test_cap_rejected_returns_400(
    alice_client: AsyncClient,
    alice_new_item_data: ItemData,
    cap_verify_result: bool,
):
    resp = await alice_client.post("/api/v1/me/items", json=alice_new_item_data)
    assert resp.status_code == 400
    assert resp.json()["message"] == "INVALID_SUBMISSION"


async def test_rate_limit_auth_returns_429(
    alice_client: AsyncClient,
    alice_new_item_data: ItemData,
    tight_rate_limit_factory,
):
    tight_rate_limit_factory(
        dep=rate_limit_item_create,
        key_prefix="item-create-test",
        anon_limit=1, auth_limit=2, window_seconds=60,
    )
    r1 = await alice_client.post("/api/v1/me/items", json=alice_new_item_data)
    r2 = await alice_client.post("/api/v1/me/items", json=alice_new_item_data)
    r3 = await alice_client.post("/api/v1/me/items", json=alice_new_item_data)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r3.status_code == 429
```

The `tests/item/` directory has a class-scoped `database` fixture override; verify the antibot fixture's autouse cap stub still functions (it's function-scoped autouse, which is compatible).

- [ ] **Step 10.4: Verify the new tests fail**

Run: `pytest tests/item/test_item_create_antibot.py -v`
Expected: FAIL (`ImportError: rate_limit_item_create`).

- [ ] **Step 10.5: Modify `routers/v1/me/items/create.py`**

Replace the file content with:

```python
from typing import TYPE_CHECKING, Annotated

from fastapi import Body, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.item import services as item_services
from babytroc.domains.item.schemas.create import ItemCreate
from babytroc.domains.item.schemas.read import ItemRead
from babytroc.infrastructure.database import get_db_session
from babytroc.routers.v1.auth import client_id_annotation
from babytroc.shared.antibot import AntiBotMixin, verify_antibot
from babytroc.shared.rate_limit import make_rate_limit_dep

from .router import router

if TYPE_CHECKING:
    from babytroc.infrastructure.config import Config


class ItemCreateRequest(AntiBotMixin, ItemCreate):
    pass


rate_limit_item_create = make_rate_limit_dep(
    key_prefix="item_create",
    extract_config=lambda c: c.item_create,
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_client_item(
    client_id: client_id_annotation,
    item_create_request: Annotated[
        ItemCreateRequest,
        Body(title="Fields for the item creation."),
    ],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    _rate_limited: Annotated[None, Depends(rate_limit_item_create)],
) -> ItemRead:
    """Create an item owned by the client."""

    config: Config = request.app.state.config
    await verify_antibot(item_create_request, config.cap)

    item_create = ItemCreate.model_validate(
        item_create_request.model_dump(exclude={"cap_token", "website"}),
    )

    return await item_services.create_item(
        db=db,
        owner_id=client_id,
        item_create=item_create,
    )
```

Note: `ItemCreate` has a `@field_serializer` and a `@field_validator` on `regions`. `model_dump` round-tripping through `model_validate` must preserve the `set[int]` semantics. Verify by running the happy-path test; if it fails, switch to `ItemCreate(**{...})` explicit construction passing only the keys present.

Alternative if `model_dump`/`model_validate` round-trip is lossy: use `ItemCreate.model_construct(...)` cautiously, or build the kwargs dict explicitly:

```python
item_create = ItemCreate(
    name=item_create_request.name,
    description=item_create_request.description,
    images=item_create_request.images,
    targeted_age_months=item_create_request.targeted_age_months,
    regions=item_create_request.regions,
    blocked=item_create_request.blocked,
    categories=item_create_request.categories,
)
```

Prefer the explicit constructor form if there's any doubt. Use the round-trip form only if the explicit form is verified equivalent.

- [ ] **Step 10.6: Run new + existing item-create tests**

Run: `pytest tests/item/test_item_create_antibot.py tests/item/test_item_create.py -v`
Expected: PASS.

- [ ] **Step 10.7: Run the full item-test suite**

Run: `pytest tests/item/ -v`
Expected: PASS (after the fixture updates from Step 10.2).

- [ ] **Step 10.8: Commit**

```bash
git add src/babytroc/routers/v1/me/items/create.py tests/fixtures/items.py tests/item/
git commit -m "feat(item): add antibot + rate-limit to item creation"
```

---

## Task 11: Add rate-limit to `POST /api/v1/images`

**Files:**
- Modify: `src/babytroc/routers/v1/images/create.py`
- Create: `tests/image/__init__.py` (or use existing item/image tests location)
- Create: `tests/image/test_image_upload_rate_limit.py`

- [ ] **Step 11.1: Decide the test location**

`tests/item/test_item_images.py` already exercises `POST /api/v1/images`. Two options: add to that file, or create a new `tests/image/` directory. The plan picks the latter because the new tests are about transport-level rate limiting, not item-image semantics.

Create `tests/image/__init__.py` (empty).

- [ ] **Step 11.2: Write the failing rate-limit test**

Create `tests/image/test_image_upload_rate_limit.py`:

```python
from io import BytesIO

from httpx import AsyncClient

from babytroc.routers.v1.images.create import rate_limit_image_upload


def _png_bytes() -> bytes:
    """Minimal valid PNG header — server may accept or reject as image, but
    rate-limit gate runs before image processing, so this is enough."""
    return (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xa6\xb5\xe3\xc7"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )


async def test_rate_limit_returns_429_after_limit(
    alice_client: AsyncClient,
    tight_rate_limit_factory,
):
    tight_rate_limit_factory(
        dep=rate_limit_image_upload,
        key_prefix="image-upload-test",
        anon_limit=2, auth_limit=2, window_seconds=60,
    )

    for _ in range(2):
        r = await alice_client.post(
            "/api/v1/images",
            files={"file": ("x.png", BytesIO(_png_bytes()), "image/png")},
        )
        assert r.status_code in (200, 201), r.text  # whichever the endpoint uses

    r3 = await alice_client.post(
        "/api/v1/images",
        files={"file": ("x.png", BytesIO(_png_bytes()), "image/png")},
    )
    assert r3.status_code == 429
```

Note: S3 uploads are globally mocked by `tests/fixtures/s3.py::mock_s3_uploads` per CLAUDE.md.

- [ ] **Step 11.3: Verify failure**

Run: `pytest tests/image/test_image_upload_rate_limit.py -v`
Expected: FAIL (`ImportError: rate_limit_image_upload`).

- [ ] **Step 11.4: Modify `routers/v1/images/create.py`**

Replace the file content with:

```python
from typing import Annotated

from fastapi import Depends, Request, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.image import services as image_services
from babytroc.domains.image.schemas.read import ItemImageRead
from babytroc.infrastructure.database import get_db_session
from babytroc.routers.v1.auth import client_id_annotation
from babytroc.shared.rate_limit import make_rate_limit_dep

from .router import router

# TODO limite upload size (middleware)


rate_limit_image_upload = make_rate_limit_dep(
    key_prefix="image_upload",
    extract_config=lambda c: c.image_upload,
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_image(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    file: UploadFile,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    _rate_limited: Annotated[None, Depends(rate_limit_image_upload)],
) -> ItemImageRead:
    """Upload item image."""

    return await image_services.upload_image(
        config=request.app.state.config,
        db=db,
        fp=file.file,
        owner_id=client_id,
    )
```

- [ ] **Step 11.5: Run the new test + existing image tests**

Run: `pytest tests/image/ tests/item/test_item_images.py -v`
Expected: PASS.

- [ ] **Step 11.6: Commit**

```bash
git add src/babytroc/routers/v1/images/create.py tests/image/
git commit -m "feat(image): add rate-limit to image upload endpoint"
```

---

## Task 12: Full validation

- [ ] **Step 12.1: Run lint**

Run: `mise run lint`
Expected: PASS (ruff + mypy).

If new ruff complaints appear:
- `S105` (hardcoded password): cap tokens in tests look like passwords — add `# noqa: S105` only on the specific line, not globally.
- Unused imports: remove.

If mypy complaints appear:
- The `extract_config: Callable[[Config], RateLimitConfig]` lambda may need `# type: ignore[no-untyped-def]` — prefer giving the lambdas an explicit annotation by extracting them: `_extract: Callable[[Config], RateLimitConfig] = lambda c: c.signup`.

- [ ] **Step 12.2: Run domain boundary check**

Run: `uv run babycli lint boundaries` (or `mise run babycli lint boundaries`).
Expected: PASS — `shared/antibot.py` imports `infrastructure.config` (allowed: shared can read infrastructure), routers import `shared.antibot` and `domains.*` (allowed: routers read everything).

- [ ] **Step 12.3: Run the full test suite**

Run: `mise run test`
Expected: PASS.

If any test fails for reasons unrelated to this work (e.g. a flake), rerun only that test. If it fails repeatedly, investigate before claiming done.

- [ ] **Step 12.4: Verify the new env vars are documented**

The spec's "Migration / operator setup" section enumerates the new optional env vars. Verify they appear in `src/babytroc/infrastructure/config.py` docstrings/comments or `.env.yaml.example` if such a file exists. If `.env.yaml` (referenced in `mise.toml`) has documented env vars, append the new ones with their defaults.

Run: `grep -l '\.env\.yaml' . -r 2>/dev/null` and check if a template file exists.

- [ ] **Step 12.5: Final commit if doc/env changes were needed**

```bash
git add <files>
git commit -m "docs: document new rate-limit env vars"
```

- [ ] **Step 12.6: Summary report**

Confirm in the conversation that:
1. All 12 tasks completed.
2. Full test suite passes (`mise run test`).
3. Lint passes (`mise run lint`).
4. Boundary check passes.
5. Five endpoints now share the antibot + rate-limit pipeline; service layer unchanged.

---

## Notes for the executor

- **Frequent commits.** Every task ends with a commit. Don't bundle.
- **Test-first.** Every endpoint task adds tests *before* the endpoint change.
- **No service signature changes.** `user_services.create_user`, `item_services.create_item`, and `auth_services.create_account_password_reset_authrorization` keep their current signatures. The router strips the antibot fields and passes only domain-layer types.
- **Pydantic v2 mixin inheritance order.** `class UserCreateRequest(AntiBotMixin, UserCreate)`. The MRO matters if either base defines `model_config`; Pydantic v2 merges configs but field ordering follows MRO. If you see a validator firing in an unexpected order, swap inheritance to `class UserCreateRequest(UserCreate, AntiBotMixin)` — the existing domain validators (name strip, password rules) must still fire.
- **Cap fixture autouse.** `tests/fixtures/antibot.py::stub_cap_verify` is autouse function-scoped. Every test runs with the stub returning True by default. Override via `@pytest.mark.parametrize("cap_verify_result", [False])` on the test function.
- **Rate-limit isolation across tests.** The `_clear_rate_limit_overrides` autouse fixture clears both `app.dependency_overrides` and any cached `_rate_limiter_*` attributes on `app.state` after each test, so default-limit tests don't see leaked tight limiters from earlier tests.
- **Order matters.** Run tasks in order; later tasks assume earlier ones landed.
