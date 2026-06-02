# Generic Redis Host (TCP / TLS / Unix Socket) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let operators configure Redis over any of three transports (plain TCP, TLS, Unix domain socket) via a canonical `REDIS_URL` env var, while keeping the existing discrete `REDIS_HOST/PORT/DB/PASSWORD` variables as a backward-compatible fallback and preserving the test fixture's per-worker `db` override.

**Architecture:** `RedisConfig` becomes a `NamedTuple` of parsed fields (`scheme`, `host`, `port`, `socket_path`, `db`, `username`, `password`) with a computed `url` property that emits the right URL format per scheme. `from_env` precedence is: explicit kwargs → `REDIS_URL` → discrete vars → defaults. Both consumers (`create_redis_client`, broadcaster) collapse onto `Redis.from_url(config.url)`, which natively handles all three schemes.

**Tech Stack:** Python 3.13, `typing.NamedTuple`, `pydantic.SecretStr`, `urllib.parse` (urlparse, parse_qs, quote, unquote), `redis.asyncio.Redis`, pytest with `patch.dict("os.environ", …)`.

---

## File Structure

**Modified:**
- `src/babytroc/infrastructure/config.py` — rewrite `RedisConfig` (lines 104-141 today). Add the new imports at the top.
- `src/babytroc/infrastructure/redis.py` — collapse `create_redis_client` to `Redis.from_url`.
- `src/babycli/config.py` — add `"REDIS_URL"` to `OPTIONAL_ENV_VARS`.
- `src/babycli/setup.py` — rewrite `_REDIS_HINTS` to surface `REDIS_URL` as the primary option.
- `CLAUDE.md` — add `REDIS_URL` to the env-var documentation.

**Created:**
- `tests/test_redis_config.py` — all new behavioral tests for `RedisConfig`.
- `tests/test_create_redis_client.py` — one focused test for the `create_redis_client` URL handoff.

**Unchanged (verified during design):**
- `src/babytroc/app.py` — already uses `Redis.from_url(config.pubsub.url, socket_timeout=None)`.
- `src/babycli/check.py` — already calls `create_redis_client(config)` indirectly.
- `tests/fixtures/app.py` — `RedisConfig.from_env(db=redis_db)` continues to work because `db` remains a top-level field.
- `tests/test_cache.py`, `tests/test_cache_invalidation.py` — independent of `RedisConfig`.

---

## Task 1: Rewrite `RedisConfig` with URL/discrete-var hybrid

**Files:**
- Modify: `src/babytroc/infrastructure/config.py:104-141` (the existing `RedisConfig` class)
- Test: `tests/test_redis_config.py` (new file)

This is the biggest task — done TDD, one test at a time. We write all failing tests first, then a single implementation pass, then verify.

### Step 1.1: Create the test file scaffold and confirm it loads

- [ ] **Create `tests/test_redis_config.py` with imports and an empty marker test**

```python
from unittest.mock import patch

import pytest
from pydantic import SecretStr

from babytroc.infrastructure.config import RedisConfig


class TestRedisConfigFromEnv:
    pass


class TestRedisConfigUrl:
    pass


class TestRedisConfigValidation:
    pass
```

- [ ] **Confirm it collects without errors**

Run: `pytest tests/test_redis_config.py --collect-only -q`
Expected: 0 tests collected, exit 0 (no import errors).

### Step 1.2: Test — discrete vars fallback (current default behavior)

- [ ] **Add to `TestRedisConfigFromEnv`:**

```python
    def test_defaults_when_no_env(self):
        with patch.dict("os.environ", {}, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.scheme == "redis"
        assert cfg.host == "localhost"
        assert cfg.port == 6379
        assert cfg.db == 0
        assert cfg.username == ""
        assert cfg.password.get_secret_value() == ""
        assert cfg.socket_path is None

    def test_discrete_vars(self):
        env = {
            "REDIS_HOST": "redis.internal",
            "REDIS_PORT": "6390",
            "REDIS_DB": "5",
            "REDIS_PASSWORD": "s3cret",
        }
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.scheme == "redis"
        assert cfg.host == "redis.internal"
        assert cfg.port == 6390
        assert cfg.db == 5
        assert cfg.password.get_secret_value() == "s3cret"
        assert cfg.socket_path is None
```

- [ ] **Run to verify failure**

Run: `pytest tests/test_redis_config.py::TestRedisConfigFromEnv -v`
Expected: FAIL — `cfg.scheme`, `cfg.username`, or `cfg.socket_path` attributes don't exist on the current `RedisConfig`.

### Step 1.3: Test — REDIS_URL with `redis://` scheme

- [ ] **Add to `TestRedisConfigFromEnv`:**

```python
    def test_redis_url_tcp(self):
        env = {"REDIS_URL": "redis://r.example.com:6380/3"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.scheme == "redis"
        assert cfg.host == "r.example.com"
        assert cfg.port == 6380
        assert cfg.db == 3
        assert cfg.socket_path is None

    def test_redis_url_defaults_port_and_db(self):
        env = {"REDIS_URL": "redis://r.example.com"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.port == 6379
        assert cfg.db == 0
```

- [ ] **Run to verify failure**

Run: `pytest tests/test_redis_config.py::TestRedisConfigFromEnv -v`
Expected: FAIL — `RedisConfig.from_env` doesn't read `REDIS_URL` yet.

### Step 1.4: Test — REDIS_URL with `rediss://` (TLS)

- [ ] **Add to `TestRedisConfigFromEnv`:**

```python
    def test_redis_url_tls(self):
        env = {"REDIS_URL": "rediss://r.example.com:6380/0"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.scheme == "rediss"
        assert cfg.host == "r.example.com"
        assert cfg.port == 6380
        assert cfg.db == 0
```

- [ ] **Run to verify failure**

Run: `pytest tests/test_redis_config.py::TestRedisConfigFromEnv::test_redis_url_tls -v`
Expected: FAIL.

### Step 1.5: Test — REDIS_URL with `unix://` scheme

- [ ] **Add to `TestRedisConfigFromEnv`:**

```python
    def test_redis_url_unix_with_db_query(self):
        env = {"REDIS_URL": "unix:///tmp/redis.sock?db=2"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.scheme == "unix"
        assert cfg.socket_path == "/tmp/redis.sock"
        assert cfg.db == 2
        assert cfg.host is None
        assert cfg.port is None

    def test_redis_url_unix_db_defaults_to_zero(self):
        env = {"REDIS_URL": "unix:///var/run/redis.sock"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.socket_path == "/var/run/redis.sock"
        assert cfg.db == 0
```

- [ ] **Run to verify failure**

Run: `pytest tests/test_redis_config.py::TestRedisConfigFromEnv -v -k unix`
Expected: FAIL.

### Step 1.6: Test — username/password in URL (encoded)

- [ ] **Add to `TestRedisConfigFromEnv`:**

```python
    def test_redis_url_user_and_password_decoded(self):
        env = {"REDIS_URL": "redis://alice:p%40ss%2Fword@host:6379/0"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.username == "alice"
        assert cfg.password.get_secret_value() == "p@ss/word"

    def test_redis_url_password_only(self):
        env = {"REDIS_URL": "redis://:onlypass@host:6379/0"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.username == ""
        assert cfg.password.get_secret_value() == "onlypass"
```

- [ ] **Run to verify failure**

Run: `pytest tests/test_redis_config.py::TestRedisConfigFromEnv -v -k password`
Expected: FAIL.

### Step 1.7: Test — `db=` keyword override preserved for all three schemes

This is the critical compatibility test for `tests/fixtures/app.py:30`.

- [ ] **Add to `TestRedisConfigFromEnv`:**

```python
    def test_db_kwarg_overrides_redis_url_path(self):
        env = {"REDIS_URL": "redis://r.example.com:6380/3"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env(db=9)
        assert cfg.db == 9
        assert cfg.url == "redis://r.example.com:6380/9"

    def test_db_kwarg_overrides_unix_url_query(self):
        env = {"REDIS_URL": "unix:///tmp/redis.sock?db=2"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env(db=9)
        assert cfg.db == 9
        assert cfg.url == "unix:///tmp/redis.sock?db=9"

    def test_db_kwarg_overrides_discrete_vars(self):
        env = {"REDIS_HOST": "r.example.com", "REDIS_DB": "3"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env(db=9)
        assert cfg.db == 9
```

- [ ] **Run to verify failure**

Run: `pytest tests/test_redis_config.py::TestRedisConfigFromEnv -v -k override`
Expected: FAIL.

### Step 1.8: Tests — `url` property round-trips for each scheme

- [ ] **Add to `TestRedisConfigUrl`:**

```python
    def test_url_redis(self):
        cfg = RedisConfig(
            scheme="redis",
            host="h.example.com",
            port=6379,
            socket_path=None,
            db=2,
            username="",
            password=SecretStr(""),
        )
        assert cfg.url == "redis://h.example.com:6379/2"

    def test_url_rediss(self):
        cfg = RedisConfig(
            scheme="rediss",
            host="h.example.com",
            port=6380,
            socket_path=None,
            db=0,
            username="",
            password=SecretStr(""),
        )
        assert cfg.url == "rediss://h.example.com:6380/0"

    def test_url_unix(self):
        cfg = RedisConfig(
            scheme="unix",
            host=None,
            port=None,
            socket_path="/tmp/redis.sock",
            db=3,
            username="",
            password=SecretStr(""),
        )
        assert cfg.url == "unix:///tmp/redis.sock?db=3"

    def test_url_with_password_only(self):
        cfg = RedisConfig(
            scheme="redis",
            host="h",
            port=6379,
            socket_path=None,
            db=0,
            username="",
            password=SecretStr("p@ss"),
        )
        assert cfg.url == "redis://:p%40ss@h:6379/0"

    def test_url_with_user_and_password(self):
        cfg = RedisConfig(
            scheme="redis",
            host="h",
            port=6379,
            socket_path=None,
            db=0,
            username="alice",
            password=SecretStr("p/w"),
        )
        assert cfg.url == "redis://alice:p%2Fw@h:6379/0"

    def test_url_with_username_only(self):
        cfg = RedisConfig(
            scheme="redis",
            host="h",
            port=6379,
            socket_path=None,
            db=0,
            username="alice",
            password=SecretStr(""),
        )
        assert cfg.url == "redis://alice@h:6379/0"
```

- [ ] **Run to verify failure**

Run: `pytest tests/test_redis_config.py::TestRedisConfigUrl -v`
Expected: FAIL — `RedisConfig` lacks the new fields.

### Step 1.9: Tests — invalid input raises

- [ ] **Add to `TestRedisConfigValidation`:**

```python
    def test_invalid_scheme_raises(self):
        env = {"REDIS_URL": "http://nope.example.com"}
        with patch.dict("os.environ", env, clear=True), pytest.raises(ValueError, match="scheme"):
            RedisConfig.from_env()

    def test_unix_url_without_path_raises(self):
        env = {"REDIS_URL": "unix://"}
        with patch.dict("os.environ", env, clear=True), pytest.raises(ValueError, match="socket"):
            RedisConfig.from_env()

    def test_redis_url_without_host_raises(self):
        env = {"REDIS_URL": "redis:///0"}
        with patch.dict("os.environ", env, clear=True), pytest.raises(ValueError, match="host"):
            RedisConfig.from_env()

    def test_password_redacted_in_repr(self):
        env = {"REDIS_URL": "redis://:supersecret@h:6379/0"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert "supersecret" not in repr(cfg)
```

- [ ] **Run to verify failure**

Run: `pytest tests/test_redis_config.py::TestRedisConfigValidation -v`
Expected: FAIL.

### Step 1.10: Implement the new `RedisConfig`

- [ ] **Open `src/babytroc/infrastructure/config.py` and add imports near the top**

After the existing imports (around line 1-8), update to include:

```python
import os
from collections.abc import Mapping
from datetime import timedelta
from typing import Literal, NamedTuple, Self
from urllib.parse import parse_qs, quote, unquote, urlparse

import sqlalchemy
from pydantic import SecretStr
```

(Add `Literal` to the typing import, add the `urllib.parse` line.)

- [ ] **Replace the `RedisConfig` class (lines 104-141 today) with this implementation**

```python
class RedisConfig(NamedTuple):
    scheme: Literal["redis", "rediss", "unix"]
    host: str | None
    port: int | None
    socket_path: str | None
    db: int
    username: str
    password: SecretStr

    @classmethod
    def from_env(  # noqa: C901
        cls,
        *,
        url: str | None = None,
        scheme: Literal["redis", "rediss", "unix"] | None = None,
        host: str | None = None,
        port: int | None = None,
        socket_path: str | None = None,
        db: int | None = None,
        username: str | None = None,
        password: SecretStr | str | None = None,
        test: bool | None = None,
    ) -> Self:
        env = EnvironmentVariablesReader(test=test)

        # 1. Source fields from explicit url arg, REDIS_URL, or discrete vars.
        if url is None:
            url = env.get("REDIS_URL")

        parsed_scheme: Literal["redis", "rediss", "unix"]
        parsed_host: str | None
        parsed_port: int | None
        parsed_socket_path: str | None
        parsed_db: int
        parsed_username: str
        parsed_password: str

        if url:
            (
                parsed_scheme,
                parsed_host,
                parsed_port,
                parsed_socket_path,
                parsed_db,
                parsed_username,
                parsed_password,
            ) = cls._parse_url(url)
        else:
            parsed_scheme = "redis"
            parsed_host = env.get("REDIS_HOST", default="localhost")
            parsed_port = int(env.get("REDIS_PORT", default="6379"))
            parsed_socket_path = None
            parsed_db = int(env.get("REDIS_DB", default="0"))
            parsed_username = ""
            parsed_password = env.get("REDIS_PASSWORD", default="")

        # 2. Per-field kwarg overrides win over both URL and discrete vars.
        final_scheme = scheme if scheme is not None else parsed_scheme
        final_host = host if host is not None else parsed_host
        final_port = port if port is not None else parsed_port
        final_socket_path = (
            socket_path if socket_path is not None else parsed_socket_path
        )
        final_db = db if db is not None else parsed_db
        final_username = username if username is not None else parsed_username
        if password is None:
            final_password = SecretStr(parsed_password)
        elif isinstance(password, str):
            final_password = SecretStr(password)
        else:
            final_password = password

        # 3. Validate scheme-specific invariants.
        if final_scheme == "unix":
            if not final_socket_path:
                msg = "Redis unix scheme requires a socket path"
                raise ValueError(msg)
            final_host = None
            final_port = None
        else:
            if not final_host:
                msg = f"Redis {final_scheme} scheme requires a host"
                raise ValueError(msg)
            if final_port is None or final_port <= 0:
                msg = f"Redis {final_scheme} scheme requires a positive port"
                raise ValueError(msg)
            final_socket_path = None

        return cls(
            scheme=final_scheme,
            host=final_host,
            port=final_port,
            socket_path=final_socket_path,
            db=final_db,
            username=final_username,
            password=final_password,
        )

    @staticmethod
    def _parse_url(
        url_str: str,
    ) -> tuple[
        Literal["redis", "rediss", "unix"],
        str | None,
        int | None,
        str | None,
        int,
        str,
        str,
    ]:
        parsed = urlparse(url_str)
        if parsed.scheme not in ("redis", "rediss", "unix"):
            msg = (
                f"Unsupported Redis URL scheme {parsed.scheme!r}; "
                "expected one of: redis, rediss, unix"
            )
            raise ValueError(msg)
        scheme: Literal["redis", "rediss", "unix"] = parsed.scheme  # type: ignore[assignment]

        username = unquote(parsed.username) if parsed.username else ""
        password = unquote(parsed.password) if parsed.password else ""

        if scheme == "unix":
            socket_path = parsed.path or ""
            if not socket_path:
                msg = "Redis unix URL requires a socket path"
                raise ValueError(msg)
            db_values = parse_qs(parsed.query).get("db", ["0"])
            db = int(db_values[0])
            return scheme, None, None, socket_path, db, username, password

        host = parsed.hostname
        if not host:
            msg = f"Redis {scheme} URL requires a host"
            raise ValueError(msg)
        port = parsed.port if parsed.port is not None else 6379
        db_path = parsed.path.lstrip("/") if parsed.path else ""
        db = int(db_path) if db_path else 0
        return scheme, host, port, None, db, username, password

    @property
    def url(self) -> str:
        user = self.username
        pwd = self.password.get_secret_value()
        if user and pwd:
            auth = f"{quote(user, safe='')}:{quote(pwd, safe='')}@"
        elif pwd:
            auth = f":{quote(pwd, safe='')}@"
        elif user:
            auth = f"{quote(user, safe='')}@"
        else:
            auth = ""

        if self.scheme == "unix":
            return f"unix://{auth}{self.socket_path}?db={self.db}"
        return f"{self.scheme}://{auth}{self.host}:{self.port}/{self.db}"
```

- [ ] **Run the new tests to verify they all pass**

Run: `pytest tests/test_redis_config.py -v`
Expected: all tests in `TestRedisConfigFromEnv`, `TestRedisConfigUrl`, `TestRedisConfigValidation` PASS.

- [ ] **Run the existing config tests to verify no regression**

Run: `pytest tests/test_config.py -v`
Expected: all PASS (these tests don't touch `RedisConfig` directly but `Config.from_env` builds one).

### Step 1.11: Commit

- [ ] **Stage and commit**

```bash
git add src/babytroc/infrastructure/config.py tests/test_redis_config.py
git commit -m "$(cat <<'EOF'
feat(config): generic RedisConfig with REDIS_URL precedence

Adds support for redis://, rediss://, and unix:// URLs via a new
REDIS_URL env var. Falls back to existing REDIS_HOST/PORT/DB/PASSWORD
discrete vars when REDIS_URL is unset. Preserves per-field kwarg
overrides (used by the test fixture for xdist worker DB isolation).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Simplify `create_redis_client` to use `Redis.from_url`

**Files:**
- Modify: `src/babytroc/infrastructure/redis.py`
- Test: `tests/test_create_redis_client.py` (new file)

### Step 2.1: Write the failing test

- [ ] **Create `tests/test_create_redis_client.py`**

```python
from unittest.mock import patch

from pydantic import SecretStr

from babytroc.infrastructure.config import RedisConfig
from babytroc.infrastructure.redis import create_redis_client


class TestCreateRedisClient:
    def test_uses_from_url_with_config_url(self):
        cfg = RedisConfig(
            scheme="unix",
            host=None,
            port=None,
            socket_path="/tmp/redis.sock",
            db=4,
            username="",
            password=SecretStr(""),
        )
        with patch(
            "babytroc.infrastructure.redis.Redis.from_url",
        ) as mock_from_url:
            create_redis_client(cfg)
        mock_from_url.assert_called_once_with("unix:///tmp/redis.sock?db=4")

    def test_uses_from_url_with_tcp(self):
        cfg = RedisConfig(
            scheme="redis",
            host="h.example.com",
            port=6390,
            socket_path=None,
            db=2,
            username="",
            password=SecretStr("pw"),
        )
        with patch(
            "babytroc.infrastructure.redis.Redis.from_url",
        ) as mock_from_url:
            create_redis_client(cfg)
        mock_from_url.assert_called_once_with("redis://:pw@h.example.com:6390/2")
```

- [ ] **Run to verify failure**

Run: `pytest tests/test_create_redis_client.py -v`
Expected: FAIL — current `create_redis_client` uses kwarg construction, not `from_url`.

### Step 2.2: Replace the implementation

- [ ] **Replace the entire body of `src/babytroc/infrastructure/redis.py` with:**

```python
from redis.asyncio import Redis

from babytroc.infrastructure.config import RedisConfig


def create_redis_client(config: RedisConfig) -> Redis:
    return Redis.from_url(config.url)
```

- [ ] **Run the new test to verify it passes**

Run: `pytest tests/test_create_redis_client.py -v`
Expected: PASS (both tests).

- [ ] **Run the cache tests to confirm nothing broke**

Run: `pytest tests/test_cache.py tests/test_cache_invalidation.py -v`
Expected: PASS.

### Step 2.3: Commit

- [ ] **Stage and commit**

```bash
git add src/babytroc/infrastructure/redis.py tests/test_create_redis_client.py
git commit -m "$(cat <<'EOF'
refactor(redis): use Redis.from_url in create_redis_client

Collapses per-kwarg construction to from_url so the client transparently
supports redis://, rediss://, and unix:// schemes through redis-py.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Add `REDIS_URL` to babycli config show

**Files:**
- Modify: `src/babycli/config.py:40-46`

### Step 3.1: Add the key

- [ ] **Edit `OPTIONAL_ENV_VARS` to include `REDIS_URL` as the first redis entry**

Replace lines 40-46 with:

```python
OPTIONAL_ENV_VARS = [
    "DELAY",
    "REDIS_URL",
    "REDIS_HOST",
    "REDIS_PORT",
    "REDIS_DB",
    "REDIS_PASSWORD",
]
```

- [ ] **Verify the CLI shows the new key**

Run: `REDIS_URL=redis://localhost:6379/0 uv run babycli config show 2>&1 | grep REDIS`
Expected output includes a line like `REDIS_URL = redis://localhost:6379/0` (or the redacted form if `redact_secrets` masks URLs).

### Step 3.2: Commit

- [ ] **Stage and commit**

```bash
git add src/babycli/config.py
git commit -m "$(cat <<'EOF'
feat(babycli): show REDIS_URL in config listing

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Update babycli setup hints

**Files:**
- Modify: `src/babycli/setup.py:33-40` (`_REDIS_HINTS`)

### Step 4.1: Rewrite the hints block

- [ ] **Replace `_REDIS_HINTS` (lines 33-40) with:**

```python
_REDIS_HINTS = """\
  Install Redis:
    apt:    sudo apt install redis-server
    brew:   brew install redis
    docker: docker run -d --name redis -p 6379:6379 redis:7

  Optional env vars:
    REDIS_URL (preferred):
      redis://[user:pass@]host:port/db
      rediss://[user:pass@]host:port/db   (TLS)
      unix://[user:pass@]/path/to/sock?db=N

    Or the TCP convenience fallback (defaults: localhost:6379/0):
      REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD"""
```

- [ ] **Confirm the file still loads**

Run: `uv run python -c "from babycli.setup import _REDIS_HINTS; print(_REDIS_HINTS)"`
Expected: prints the new hints block, no syntax errors.

### Step 4.2: Commit

- [ ] **Stage and commit**

```bash
git add src/babycli/setup.py
git commit -m "$(cat <<'EOF'
docs(babycli): surface REDIS_URL in setup hints

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Document `REDIS_URL` in `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md` (the `### Environment` section, the line that lists optional Redis vars)

### Step 5.1: Locate and update the env-var documentation

- [ ] **Find the optional-env-var list in `CLAUDE.md` and update the Redis entry**

Search for the substring `REDIS_{HOST,PORT,DB,PASSWORD}` in `CLAUDE.md`. The current line reads:

```
Optional: `DELAY` (artificial request delay middleware), `REDIS_{HOST,PORT,DB,PASSWORD}` (defaults: localhost, 6379, 0, none), ...
```

Replace with:

```
Optional: `DELAY` (artificial request delay middleware), `REDIS_URL` (full connection URL: `redis://`, `rediss://`, or `unix:///path?db=N`; takes precedence over discrete vars), `REDIS_{HOST,PORT,DB,PASSWORD}` (TCP fallback, defaults: localhost, 6379, 0, none), ...
```

Use the Edit tool with a unique `old_string` (include surrounding context if needed to make it unique).

### Step 5.2: Commit

- [ ] **Stage and commit**

```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs: document REDIS_URL env var

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Verify full lint and test suite pass

**Files:** none modified — this is a verification gate.

### Step 6.1: Run lint

- [ ] **Run ruff and mypy**

Run: `mise run lint`
Expected: ruff and mypy both pass with no errors. If ruff complains about line length in the new config, reformat; if mypy complains about the `Literal` type narrowing in `_parse_url`, the `# type: ignore[assignment]` annotation already present handles it.

### Step 6.2: Run the full test suite

- [ ] **Run pytest**

Run: `mise run test`
Expected: all tests pass. Pay particular attention to:
- `tests/test_redis_config.py` and `tests/test_create_redis_client.py` (new) — must all pass.
- `tests/test_cache.py`, `tests/test_cache_invalidation.py`, `tests/test_websocket.py` — must still pass (verify per-worker DB isolation through `tests/fixtures/app.py` is intact).
- `tests/test_config.py` — must still pass.

### Step 6.3: Manual smoke test with REDIS_URL

- [ ] **Confirm the config builds end-to-end with a `REDIS_URL` set**

Run: `REDIS_URL=redis://localhost:6379/0 uv run python -c "from babytroc.infrastructure.config import Config; c = Config.from_env(); print(c.redis.url); print(c.pubsub.url)"`

Expected output:
```
redis://localhost:6379/0
redis://localhost:6379/0
```

(Requires the other required env vars to be set, e.g. via `mise` loading `.env.yaml`.)

### Step 6.4: Final review

- [ ] **Confirm no uncommitted changes remain**

Run: `git status`
Expected: clean working tree.

- [ ] **Skim the commit log**

Run: `git log --oneline -n 6`
Expected: five commits (config, redis client, babycli config, babycli setup, docs) plus the prior spec commit.

---

## Notes for the Implementer

- **Why `Redis.from_url` for both consumers?** It is the only `redis-py` API that natively handles all three schemes (TLS via stdlib defaults for `rediss://`, `unix_socket_path` parsing for `unix://`). Switching `create_redis_client` to it removes per-scheme branching from our code entirely.
- **Why validate in `from_env` and not in `__new__`?** The rest of the codebase's config classes only validate at the `from_env` boundary, and overriding `__new__` on a `NamedTuple` is awkward. The test fixture at `tests/fixtures/app.py:30` only ever calls `from_env`, so the invariant is enforced where it matters.
- **Why URL-encode credentials but not socket paths?** `urllib.parse.urlparse(...).path` returns the path unquoted; emitting it verbatim produces a URL that `urlparse` will round-trip cleanly. Credentials, on the other hand, can legitimately contain reserved characters like `@`, `:`, `/`, so they go through `quote(..., safe='')`.
- **What if a test wants to construct a malformed `RedisConfig` directly?** The `NamedTuple` constructor doesn't validate. That's intentional and matches the rest of the codebase; the test suite only exercises the `from_env` path.
