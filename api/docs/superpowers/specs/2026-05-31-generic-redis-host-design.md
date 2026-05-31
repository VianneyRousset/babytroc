# Generic Redis Host (TCP / TLS / Unix Socket)

## Goal

Let operators point the API at Redis over any of three transports — plain TCP (`redis://`), TLS (`rediss://`), or a Unix domain socket (`unix:///path`) — via a single, canonical `REDIS_URL` env var, without breaking the existing discrete-variable configuration that current deployments and tests rely on.

## Non-Goals

- TLS knobs beyond what `rediss://` provides through stdlib defaults (no custom CA file, no `ssl_cert_reqs` override). If needed later, they layer on as discrete optional vars.
- Mixing a partial `REDIS_URL` with discrete-var overrides for username/password/host/port. The URL, when set, is canonical.
- Any rename or removal of existing env vars.

## Current State

- `RedisConfig` (`src/babytroc/infrastructure/config.py:104-141`) is a `NamedTuple` of `host`, `port`, `db`, `password`. Its `url` property emits a fixed `redis://[:password@]host:port/db` string.
- `from_env` reads `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` / `REDIS_PASSWORD` with defaults `localhost` / `6379` / `0` / `""`.
- Two consumers:
  - `create_redis_client(config)` (`infrastructure/redis.py`) constructs `Redis(host=, port=, db=, password=)` directly.
  - `app.py:104` builds the broadcaster's pubsub connection with `Redis.from_url(config.pubsub.url, socket_timeout=None)`. `PubsubConfig.from_env(url=redis.url)` feeds that URL.
- Test fixture (`tests/fixtures/app.py:30`) constructs `RedisConfig.from_env(db=redis_db)`, overriding the DB per xdist worker. Any new shape must preserve that override path.
- `babycli/config.py:42-45` lists `REDIS_HOST/PORT/DB/PASSWORD` as the known keys for `babycli config show`. `babycli/setup.py:33` (`_REDIS_HINTS`) names the same vars.

## Design

### Config schema

```python
class RedisConfig(NamedTuple):
    scheme: Literal["redis", "rediss", "unix"]
    host: str | None         # None when scheme == "unix"
    port: int | None         # None when scheme == "unix"
    socket_path: str | None  # set when scheme == "unix", None otherwise
    db: int
    username: str            # default ""
    password: SecretStr      # default SecretStr("")
```

**Invariant** — enforced by a `_validate()` helper called from `from_env` and from any other constructor path:

- `scheme == "unix"` ⇒ `socket_path` is a non-empty string, `host` and `port` are `None`.
- `scheme in {"redis", "rediss"}` ⇒ `host` is a non-empty string and `port` is a positive int, `socket_path` is `None`.

Violation raises a `ValueError` (or a config-specific subclass) at startup, not on first connect.

`password` is wrapped in `SecretStr` (matching `DatabaseConfig`) so it stays out of logs/reprs. `username` is a plain `str` defaulting to `""`; both empty values are treated as "no auth component."

### `url` property

Centralizes scheme-specific formatting so consumers only ever see one string:

- `redis` / `rediss`: `{scheme}://{auth}{host}:{port}/{db}`
- `unix`: `unix://{auth}{socket_path}?db={db}`

Where `{auth}` is:

- `""` when both `username` and `password` are empty.
- `":{password}@"` when only `password` is set.
- `"{username}:{password}@"` when `username` is set (with or without password).

URL-encode `username` and `password` (via `urllib.parse.quote`) so credentials containing `@`, `:`, `/`, etc. survive the round-trip. `socket_path` is emitted verbatim — it is an absolute filesystem path and `urllib.parse.urlparse` returns it unquoted from the `path` attribute.

### `from_env` precedence

```
1. If REDIS_URL is set: parse it (urllib.parse.urlparse).
2. Else: read REDIS_HOST / REDIS_PORT / REDIS_DB / REDIS_PASSWORD
        with existing defaults; scheme := "redis".
3. Apply keyword overrides last (e.g. db=N from the test fixture).
4. Validate invariants; raise on inconsistency.
```

URL parsing:

- Scheme must be one of `{"redis", "rediss", "unix"}`. Anything else raises a clear config error naming the offending scheme and the env var.
- For `redis` / `rediss`: extract `hostname`, `port` (default `6379` if absent), `username` (default `""`), `password` (default `""`), and `db` from the path (`"/3"` → `3`; missing or `"/"` → `0`).
- For `unix`: extract `path` (after the authority) as `socket_path`; `db` comes from the `db` query parameter (default `0`); `host` / `port` stay `None`.
- `urllib.parse` returns `None` for absent components — normalize all to the field's default (`""` for username/password, `0` for db).

Test-mode `TEST_REDIS_URL` is read transparently by the existing `EnvironmentVariablesReader` (it already does the `TEST_` prefix lookup).

### Keyword overrides

Signature:

```python
@classmethod
def from_env(
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
) -> Self: ...
```

`url`, when passed explicitly, takes precedence over `REDIS_URL`. Per-field kwargs override their respective parsed/read values. Order: explicit `url` arg → `REDIS_URL` → discrete env vars → per-field kwargs.

### Consumer changes

**`infrastructure/redis.py`** — collapse to `Redis.from_url`:

```python
def create_redis_client(config: RedisConfig) -> Redis:
    return Redis.from_url(config.url)
```

`redis.asyncio.Redis.from_url` natively handles all three schemes (TLS via stdlib defaults for `rediss://`, `unix_socket_path` parsing for `unix://`). No per-scheme branching needed in our code.

**`app.py:104`** — no change. Already uses `Redis.from_url(config.pubsub.url, socket_timeout=None)`. `config.pubsub.url` is sourced from `config.redis.url`, which now emits the correct format for any scheme.

**`babycli/config.py:42-45`** — add `"REDIS_URL"` to the known-keys list so `babycli config show` displays it alongside the discrete vars.

**`babycli/setup.py:33` (`_REDIS_HINTS`)** — update copy to name `REDIS_URL` as the primary option:

```
Env vars:
    REDIS_URL (preferred): redis://, rediss://, or unix:// URL
    REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD (TCP convenience fallback)
```

**`babycli/check.py`** — no change. `check_redis()` already goes through `create_redis_client(config)`.

### Validation behavior

- Invalid scheme in `REDIS_URL`: raise at `Config.from_env` time. Error message names the offending scheme.
- Missing `socket_path` for `unix` scheme (e.g. `unix://`): raise.
- Missing `host` for `redis`/`rediss`: raise.
- Negative or zero port: raise.
- Non-integer `db` in URL path or query: raise.

All errors surface during `Config.from_env`, before the app starts serving requests.

## Test Plan

**Existing tests — confirm no regression:**

- `tests/fixtures/app.py:30` (`RedisConfig.from_env(db=redis_db)`) — `db` override continues to work; per-worker xdist DB isolation intact.
- `tests/test_cache.py`, `tests/test_cache_invalidation.py` — independent of `RedisConfig`, no change expected.
- Full `mise run test` run passes.

**New tests** (one file: `tests/test_redis_config.py`):

- Discrete-vars fallback (no `REDIS_URL`) yields scheme `"redis"` with current defaults.
- `REDIS_URL=redis://localhost:6379/3` parses fields correctly; `url` round-trips.
- `REDIS_URL=rediss://r.example.com:6380/0` yields scheme `"rediss"`; `url` round-trips.
- `REDIS_URL=unix:///tmp/redis.sock?db=2` yields scheme `"unix"`, `socket_path="/tmp/redis.sock"`, `db=2`, `host` and `port` `None`.
- `REDIS_URL=redis://user:p%40ss@host:6379/0` populates `username="user"`, `password=SecretStr("p@ss")` (URL-decoded); `url` re-encodes correctly.
- `from_env(db=7)` override produces the right URL for each of the three schemes (path vs. query).
- Invalid scheme (`http://...`) raises a clear config error at `from_env` time.
- Constructing `RedisConfig(scheme="unix", host="x", ...)` raises (invariant).
- Constructing `RedisConfig(scheme="redis", host=None, ...)` raises (invariant).
- `password` survives round-trip without leaking in `repr(config)` (sanity check on `SecretStr`).

## Migration / Rollout

- No env-var rename or removal.
- Existing `.env.yaml` (which sets `REDIS_HOST/PORT/DB`, `TEST_REDIS_DB`) continues to work unchanged — covered by the discrete-vars fallback test.
- Update `CLAUDE.md` env-var list to mention `REDIS_URL` as optional.
- Update `babycli/setup.py` hints (above).
- No alembic, no data migration.

## Files Touched

- `src/babytroc/infrastructure/config.py` — `RedisConfig` rewrite.
- `src/babytroc/infrastructure/redis.py` — `create_redis_client` simplification.
- `src/babycli/config.py` — known-keys list.
- `src/babycli/setup.py` — `_REDIS_HINTS` copy.
- `tests/test_redis_config.py` — new test file.
- `CLAUDE.md` — env-var documentation.
