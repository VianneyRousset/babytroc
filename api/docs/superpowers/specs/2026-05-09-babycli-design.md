# babycli — Babytroc Operations CLI

**Date:** 2026-05-09
**Status:** Approved
**Branch:** refactor/ddd-lite-restructure

## Overview

Unified CLI for Babytroc API operations: onboarding, health checks, DB management, server control, admin user ops, stats, code quality checks, and config inspection. Absorbs existing `seed` module. Runs everywhere — dev, staging, production.

Invoked via `mise run babycli` (behind `uv run python -m babycli`).

## Package Layout

```
babycli/
  __main__.py          # root cyclopts App, mounts all subcommand groups
  setup.py             # guided onboarding wizard
  db.py                # migrations, seed, status, reset
  server.py            # start uvicorn
  check.py             # runtime health checks (postgres, redis, s3, email, migrations)
  stats.py             # DB counts and metrics
  user.py              # admin user CRUD
  config.py            # show/validate resolved config
  lint.py              # code quality (ruff, mypy, domain boundary check)
  logs.py              # stub for future Grafana/Loki integration
  danger.py            # danger-mode session toggle + per-command --danger flag
  _utils.py            # shared helpers (colored output, DB session, subprocess runner)
```

## Entry Point

`babycli/__main__.py` creates root `cyclopts.App(name="babycli")` and mounts each subcommand group via `app.command(sub_app)`.

### mise.toml

```toml
[tasks.babycli]
description = "Run CLI tool"
run = "uv run python -m babycli"
```

Usage: `mise run babycli -- setup`, `mise run babycli -- check postgres`.

## Seed Absorption

`seed/` module stays as-is for its populate/check logic. `babycli/db.py` imports from `seed/` internals and exposes them as `babycli db seed` subcommands. `python -m seed` still works but is undocumented.

## Danger Mode

Hybrid mechanism: per-command `--danger` flag OR session-based `danger-mode enable`.

### State File

`~/.babytroc/.danger-mode` (JSON):

```json
{"enabled_at": "2026-05-09T14:30:00", "ttl_minutes": 5}
```

### Commands

| Command | Description |
|---------|------------|
| `danger-mode enable [--ttl 10]` | Create state file, default 5min TTL |
| `danger-mode disable` | Remove state file |
| `danger-mode status` | Show if active + time remaining |

### Guard Logic

- `is_danger_mode() -> bool` checks state file exists + not expired. Expired file auto-cleaned.
- Dangerous commands require: `--danger` flag passed OR `is_danger_mode()` returns True.
- Either way, interactive `[y/N]` confirmation prompt before executing.
- Commands gated: `user create`, `user delete`, `user reset-password`, `user disable`, `db reset`, `db seed --force`.

## Command Groups

### `babycli setup`

Interactive guided wizard for new users. Checks services in order:

1. **Environment vars** — scan all required vars from `Config.from_env()`, report missing with example values
2. **PostgreSQL** — try connect, report version or error + install hints (apt/brew/docker)
3. **Redis** — ping, same pattern
4. **S3/MinIO** — check bucket exists, report endpoint + hints
5. **Email** — validate config parseable (no actual send)
6. **Alembic** — check if migrations up to date

Each step: `[OK]` / `[FAIL]` with actionable fix instructions and doc/install links per platform.

`--check-only` flag: non-interactive, scriptable exit codes (0 = all good, 1 = issues found).

### `babycli db`

| Command | Danger | Description |
|---------|--------|------------|
| `db migrate` | — | `alembic upgrade head` |
| `db downgrade [revision]` | — | `alembic downgrade` |
| `db status` | — | Current revision, pending migrations |
| `db seed [--force] [-n 50]` | `--force` only | Populate dev data (absorbs `python -m seed populate all`) |
| `db seed regions` | — | Seed regions only |
| `db seed categories` | — | Seed categories only |
| `db seed users` | — | Seed users only |
| `db seed items [-n 20]` | — | Seed items only |
| `db reset` | Yes | Drop all tables, re-migrate, optionally re-seed |

### `babycli server`

| Command | Description |
|---------|------------|
| `server start` | Start uvicorn (replaces entrypoint.sh logic) |

Options: `--host` (default `0.0.0.0`), `--port` (default `8080`), `--workers`, `--reload`.

Runs `alembic upgrade head` before starting, matching current entrypoint.sh behavior.

### `babycli check`

| Command | Description |
|---------|------------|
| `check` (no args) | Run all checks |
| `check postgres` | DB connection + version |
| `check redis` | Ping |
| `check s3` | Bucket exists + permissions |
| `check email` | Config valid |
| `check migrations` | Pending migrations |

Exit codes: 0 = healthy, 1 = unhealthy. Scriptable for monitoring.

### `babycli stats`

| Command | Description |
|---------|------------|
| `stats` (no args) | All counts summary |
| `stats users` | User count, active/inactive breakdown |
| `stats items` | Item count, by category |
| `stats loans` | Loan counts by status |
| `stats chats` | Chat and message counts |

### `babycli user`

| Command | Danger | Description |
|---------|--------|------------|
| `user list [--limit] [--offset]` | — | List users |
| `user get <id>` | — | Show user details |
| `user search <query>` | — | Search by name/email |
| `user create --email --name` | Yes | Create user bypassing auth flow |
| `user disable <id>` | Yes | Disable account |
| `user enable <id>` | — | Re-enable account |
| `user reset-password <id>` | Yes | Force password reset |
| `user delete <id>` | Yes | Delete user |

### `babycli config`

| Command | Description |
|---------|------------|
| `config show` | Print resolved config, secrets redacted (`***`) |
| `config validate` | Check all required env vars present, report missing |

### `babycli lint`

| Command | Description |
|---------|------------|
| `lint` (no args) | Run all: ruff + mypy + boundary check |
| `lint ruff` | Run ruff only |
| `lint mypy` | Run mypy only |
| `lint boundaries [--strict]` | Domain boundary check (wraps `scripts/check_domain_boundaries.py`) |

Wraps existing tools — `mise run lint` stays as-is.

### `babycli logs`

Stub. Prints: "Logging not yet configured. See docs for Grafana/Loki setup."

## Shared Utilities (`_utils.py`)

### Output

- `console_ok(msg)` / `console_err(msg)` / `console_warn(msg)` — colored output (green/red/yellow)
- `[OK]` / `[FAIL]` / `[WARN]` prefixes for checks and setup
- Stats: simple string-padded tables, no external dep
- Config show: key-value list, secrets as `***`
- Danger mode: yellow warning banner when active, red for destructive prompts

### DB Session

`async_db_session()` — async context manager creating a one-off `AsyncSession` from `Config.from_env()`. Reuses `DatabaseConfig` and `create_session_maker` from `app.infrastructure` but does not depend on FastAPI dependency injection.

### Subprocess

`run_subprocess(cmd: list[str]) -> int` — run shell commands (ruff, mypy) with live stdout/stderr passthrough, return exit code.

## Dependencies

No new dependencies. Uses:
- `cyclopts` (already in dev deps)
- `sqlalchemy` + `asyncpg` (already in deps)
- `redis` (already in deps)
- `aioboto3` (already in deps)
- Standard library for everything else (colored output via ANSI codes)

## Testing

CLI commands are thin wrappers around existing logic (services, seed, subprocess calls). Testing strategy:

- **Unit tests** for `danger.py` — state file creation, TTL expiry, cleanup
- **Unit tests** for `_utils.py` — output formatting, config redaction
- **Integration tests** for `check` commands — verify they detect real service status
- **Smoke tests** for subcommands — run with `--help`, verify exit codes

Tests in `tests/babycli/`.

## Success Criteria

- `mise run babycli -- setup` guides new user through full onboarding
- All 9 command groups functional
- Danger mode hybrid (flag + session) works correctly
- `python -m seed populate all` still works (backward compat)
- `mise run babycli -- check` returns proper exit codes for monitoring
- Existing `mise run lint` / `mise run test` unaffected
