# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Babytroc API — FastAPI async backend for a baby-item lending platform. PostgreSQL via SQLAlchemy async (asyncpg). Real-time chat via Redis pubsub + `broadcaster` + websockets. Image storage via S3 (MinIO). JWT auth.

## Directory Layout

```
alembic/              # DB migration scripts + env.py
alembic.ini           # alembic config (stays at root)
src/
  babytroc/           # main API package
    app.py            # create_app factory
    main.py           # uvicorn entry (babytroc.main:application)
    domains/          # DDD-lite domain packages (auth, chat, item, loan, user, image, region, category, report)
    infrastructure/   # config, database, cache, email, pubsub, redis, storage, events
    routers/          # FastAPI route handlers (v1/)
    shared/           # base models, schemas, errors, pagination, hash
  babycli/            # operations CLI
    seed/             # dev data seeding logic
    resources/seed/   # seed data files (data.json + images)
    boundaries.py     # domain boundary violation checker
stubs/                # type stubs (wonderwords)
tests/
docs/
```

## Tooling

Task runner is `mise` (see `mise.toml`). Python 3.13, deps managed by `uv`. Virtualenv at `.venv`. Build backend is `uv_build` with `module-root = "src"`.

### Common commands

- `mise run dev` — install deps, run alembic migrations, start uvicorn via babycli
- `mise run prepare` — `alembic upgrade head`
- `mise run lint` — runs `lint:ruff` + `lint:mypy`
- `mise run lint:ruff` — `ruff check .`
- `mise run lint:mypy` — `mypy stubs src tests`
- `mise run test` — `pytest -n logical --dist loadfile --maxfail=1`
- `mise run build` — `docker build . --tag=vianneyrousset/babytroc-api`
- `mise run babycli` — run babycli operations CLI
- `mise run clear-mypy-cache`

### babycli (operations CLI)

Invoked via `uv run babycli` or `mise run babycli`. Entry point: `babycli:main`.

Key commands:
- `babycli setup` — guided onboarding wizard for new installations
- `babycli check [postgres|redis|s3|email|migrations]` — health checks (scriptable exit codes)
- `babycli db migrate|downgrade|status|reset|seed` — database management
- `babycli db seed all|regions|categories|users|items` — dev data seeding
- `babycli server start [--host --port --workers --reload]` — start uvicorn (runs migrations first)
- `babycli stats [users|items|loans|chats]` — DB counts
- `babycli user list|get|search|create|disable|enable|reset-password|delete` — admin user ops
- `babycli config show|validate` — show/validate configuration
- `babycli lint [ruff|mypy|boundaries]` — code quality checks
- `babycli danger-mode enable|disable|status` — toggle danger mode for destructive ops
- `babycli logs` — stub (future Grafana/Loki)

Destructive commands (`user create/delete/disable/reset-password`, `db reset`, `db seed --force`) require `--danger` flag or active danger mode session.

### Running a single test

`pytest tests/chat/test_chat_text.py::test_name` (pytest configured with `asyncio_mode = auto`, `timeout = 10`, `pythonpath = "src"` in `pyproject.toml`).

### Alembic

`alembic upgrade head` / `alembic revision --autogenerate -m "msg"`. Config at `alembic.ini`, versions in `alembic/versions/`. Migrations run automatically via `babycli server start`.

### Environment

Required env vars (see `src/babytroc/infrastructure/config.py`): `POSTGRES_{USER,PASSWORD,HOST,PORT,DATABASE}`, `EMAIL_{SERVER,PORT,USERNAME,PASSWORD,FROM_EMAIL,FROM_NAME}`, `S3_{ENDPOINT_URL,ACCESS_KEY,SECRET_KEY,BUCKET,PUBLIC_URL}`, `JWT_{ALGORITHM,SECRET_KEY,REFRESH_TOKEN_DURATION_DAYS,ACCESS_TOKEN_DURATION_MINUTES}`, `ACCOUNT_PASSWORD_RESET_AUTHORIZATION_DURATION_MINUTES`, `HOST_NAME`, `APP_NAME`. Optional: `DELAY` (artificial request delay middleware), `REDIS_{HOST,PORT,DB,PASSWORD}` (defaults: localhost, 6379, 0, none). `mise.toml` loads `.env.yaml` automatically.

## Architecture

### Domain structure under `src/babytroc/`

Strict layering, each layer imports only from layers below:

- `routers/` — FastAPI route handlers. Versioned under `routers/v1/`. Endpoint groups: `auth`, `items`, `me` (current-user-scoped: chats, loans, items, borrowings, saved, liked, websocket), `users`, `images`, `utils`. Routers only handle request/response translation and dependency injection — business logic lives in services.
- `domains/` — DDD-lite domain packages (`auth`, `chat`, `image`, `item`, `loan`, `region`, `category`, `user`, `report`). Each domain has `models.py`, `schemas/`, `services/`, `errors.py`, optionally `events.py` + `handlers.py`. Services take an `AsyncSession` and call models. Services raise `ApiError` subclasses rather than returning error results.
- `infrastructure/` — cross-cutting: `config.py`, `database.py`, `cache.py`, `email.py`, `pubsub.py`, `redis.py`, `storage.py`, `events.py` (event bus).
- `shared/` — base classes: `models.py` (declarative base), `schemas.py`, `errors.py`, `pagination.py`, `hash.py`.

### Event bus

`src/babytroc/infrastructure/events.py` — synchronous in-process event bus. Domains emit events via `await emit(db, event)`. Handlers registered via `@on(EventType)` decorator in `domains/*/handlers.py`. Handlers run in same transaction. Cross-domain writes go through events; cross-domain reads are allowed directly.

### Domain boundary rules

Enforced by `babycli lint boundaries`:
- Any domain may import and read-query any other domain's models
- Write operations across domains must go through events
- `handlers.py` files are exempt (they are the cross-domain write path)
- Allowed structural direct writes: auth→user, loan→item

### Real-time chat

New messages → Redis pubsub notification scheduled after commit → `broadcaster` fans out to subscribed websockets under `routers/v1/me/websocket.py`. Channel prefix per worker/deployment prevents cross-talk.

### Config

`src/babytroc/infrastructure/config.py` — nested `NamedTuple` config (`Config`, `DatabaseConfig`, `PubsubConfig`, `EmailConfig`, `S3Config`, `RedisConfig`, `AuthConfig`), all built via `from_env()` classmethods. `Config.test` is auto-set when `PYTEST_CURRENT_TEST` is in env (suppresses email sending).

## Testing

- `pytest-asyncio` in auto mode. Session-scoped event loop (`asyncio_default_*_loop_scope = "session"`).
- **Per-function DB isolation**: each test gets a fresh database cloned from a seeded template via `CREATE DATABASE ... TEMPLATE`. Template contains users (alice, bob, carol), regions, categories, and images.
- **Session-scoped app**: one FastAPI instance per xdist worker. DB session maker swapped per test via `_swap_app_db` autouse fixture. Redis flushed per test.
- **Heavy test dirs** (`tests/item/`, `tests/loan/`, `tests/chat/`): local `conftest.py` overrides `database` to class-scoped to avoid recreating 256+ items per test.
- Fixtures split across `tests/fixtures/{database,app,regions,users,clients,items,loans,websockets,chat,categories,s3}.py`, registered via `tests/conftest.py::pytest_plugins`.
- HTTP tests use `httpx.AsyncClient` over `httpx_ws.transport.ASGIWebSocketTransport`. Base URL is `https://babytroc.ch`, root path `/api` — endpoints called as `/api/v1/...`.
- Standard user fixtures: `alice`, `bob`, `carol` with matching `{name}_client` fixtures that log in via OAuth2 password grant. Prefer these over building new auth setups.
- S3 uploads mocked globally via `tests/fixtures/s3.py` (session-scoped `mock_s3_uploads`).
- `timeout = 10` per test — if a WS/broadcast test hangs, suspect a missing notify or a broadcaster channel mismatch before raising the timeout.

## Lint conventions

Ruff enabled rule groups (see `pyproject.toml`): `ASYNC, B, C, E, ERA, EM, F, G, I, N, PT, PTH, RUF, S, TCH, TID, UP, W`. Tests disable `S101` (assert) and `S311` (random). `stubs/` is excluded from ruff but included in mypy. `fastapi.Depends`/`fastapi.Query` are registered as immutable calls for bugbear.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current
