# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Babytroc API — FastAPI async backend for a baby-item lending platform. PostgreSQL via SQLAlchemy async (asyncpg). Real-time chat via Postgres `LISTEN/NOTIFY` + `broadcaster` + websockets. Image storage delegated to an `imgpush` service. JWT auth.

## Tooling

Task runner is `mise` (see `mise.toml`). Python 3.13, deps managed by `uv`. Virtualenv at `.venv`.

### Common commands

- `mise run dev` — install deps, run alembic migrations, start uvicorn via `./entrypoint.sh`
- `mise run prepare` — `alembic upgrade head`
- `mise run seed` — `python -m seed populate all` (dev data)
- `mise run lint` — runs `lint:ruff` + `lint:mypy`
- `mise run lint:ruff` — `ruff check .`
- `mise run lint:mypy` — `mypy stubs app seed tests`
- `mise run test` — `pytest -n logical --dist loadscope -maxfail=1`
- `mise run build` — `docker build . --tag=vianneyrousset/babytroc-api`
- `mise run clear-mypy-cache`

### Running a single test

`pytest tests/chat/test_chat_text.py::test_name` (pytest is configured with `asyncio_mode = auto` and `timeout = 10` in `pyproject.toml`). When running the full suite, keep `-n logical --dist loadscope` so fixtures sharing a session-scoped event loop stay on the same worker.

### Alembic

`alembic upgrade head` / `alembic revision --autogenerate -m "msg"`. Config at `alembic.ini`, versions in `alembic/versions/`. Migrations run automatically on container start (see `entrypoint.sh`).

### Environment

Required env vars (see `app/config.py`): `POSTGRES_{USER,PASSWORD,HOST,PORT,DATABASE}`, `EMAIL_{SERVER,PORT,USERNAME,PASSWORD,FROM_EMAIL,FROM_NAME}`, `IMGPUSH_{HOST,PORT}`, `JWT_{ALGORITHM,SECRET_KEY,REFRESH_TOKEN_DURATION_DAYS,ACCESS_TOKEN_DURATION_MINUTES}`, `ACCOUNT_PASSWORD_RESET_AUTHORIZATION_DURATION_MINUTES`, `HOST_NAME`, `APP_NAME`. Optional: `DELAY` (artificial request delay middleware). `mise.toml` loads `.env.yaml` automatically.

## Architecture

### Layered structure under `app/`

Strict layering, each layer imports only from layers below:

- `routers/` — FastAPI route handlers. Versioned under `routers/v1/`. Endpoint groups: `auth`, `items`, `me` (current-user-scoped: chats, loans, items, borrowings, saved, liked, websocket), `users`, `images`, `utils`. Routers only handle request/response translation and dependency injection — business logic lives in `services/`.
- `services/` — business logic, grouped by domain (`auth`, `chat`, `image`, `item`, `loan`, `region`, `user`). Services take an `AsyncSession` and call models. Subpackages split CRUD (`create.py`, `read/`, `update.py`, `delete.py`) — follow this pattern when adding new operations. Services raise `ApiError` subclasses from `app/errors/` rather than returning error results.
- `models/` — SQLAlchemy ORM models (`item/`, `chat`, `user`, `loan`, `auth`, `report`). `models/base.py` defines the declarative base.
- `schemas/` — Pydantic request/response schemas, mirroring the model domains. `schemas/utils.py` + `schemas/query.py` host shared types.
- `clients/` — external service adapters (`database/`, `email/`, `networking/` — imgpush).
- `domain/` — pure domain helpers (e.g. `star.py`).
- `errors/` — `ApiError` hierarchy per domain. All raised errors are caught by the global exception handler in `app/app.py` and serialised to JSON with `status_code`, `message`, `creation_date`.

### App lifecycle

`app/main.py` → `app/app.py::create_app` builds the `FastAPI` instance and attaches to `app.state`: `config`, `db_session_maker`, `broadcast` (pubsub), `email_client`. `create_app` also calls `define_functions_and_triggers` to install Postgres triggers on startup — specifically the `notify_chat_members_new_message` trigger on `chat_message` that `pg_notify`s `user{id}` channels. Request/websocket handlers resolve `app` via the `get_app` dependency in `app/database.py` (works for both HTTP and WS contexts) and obtain a session via `get_db_session`.

### Real-time chat

New messages hit the DB → Postgres trigger emits `NOTIFY` on `user{borrower_id}` and `user{owner_id}` → `broadcaster` (backed by Postgres LISTEN) fans out to subscribed websockets under `routers/v1/me/websocket.py`. Keep this path in mind when changing `models/chat.py`, `services/chat/`, or the websocket router — end-to-end delivery depends on the trigger, the notify payload shape (`{type, chat_message_id}`), and the broadcaster channel name matching `user{id}`.

### Config

`app/config.py` — nested `NamedTuple` config (`Config`, `DatabaseConfig`, `PubsubConfig`, `EmailConfig`, `ImgpushConfig`, `AuthConfig`), all built via `from_env()` classmethods. `Config.test` is auto-set when `PYTEST_CURRENT_TEST` is in env (suppresses email sending).

## Testing

- `pytest-asyncio` in auto mode. Session-scoped event loop (`asyncio_default_*_loop_scope = "session"`).
- Fixtures split across `tests/fixtures/{database,app,regions,users,clients,items,loans,websockets,chat}.py`, registered via `tests/conftest.py::pytest_plugins`.
- HTTP tests use `httpx.AsyncClient` over `httpx_ws.transport.ASGIWebSocketTransport` (so the same client handles HTTP + WS). Base URL is `https://babytroc.ch`, root path `/api` — endpoints are called as `/api/v1/...`.
- Standard user fixtures: `alice`, `bob`, `carol` with matching `{name}_client` fixtures that log in via `/api/v1/auth/login` (OAuth2 password grant). Prefer these over building new auth setups.
- Tests live in `tests/{chat,item,loan,user}/` plus top-level `test_auth.py`, `test_utils.py`. `tests/utils.py` holds shared helpers.
- `timeout = 10` per test — if a WS/broadcast test hangs, suspect a missing notify or a broadcaster channel mismatch before raising the timeout.

## Lint conventions

Ruff enabled rule groups (see `pyproject.toml`): `ASYNC, B, C, E, ERA, EM, F, G, I, N, PT, PTH, RUF, S, TCH, TID, UP, W`. Tests disable `S101` (assert) and `S311` (random). `stubs/` is excluded from ruff but included in mypy. `fastapi.Depends`/`fastapi.Query` are registered as immutable calls for bugbear.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current
