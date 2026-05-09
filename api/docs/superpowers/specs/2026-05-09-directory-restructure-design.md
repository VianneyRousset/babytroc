# Directory Restructure

**Date:** 2026-05-09
**Status:** Approved

## Goal

Clean up top-level directory layout. Absorb standalone `seed/` and `scripts/` into `babycli`. Remove `entrypoint.sh`. Declare seed data as package resources.

## Current → Target

### Removed

| Item | Reason |
|------|--------|
| `entrypoint.sh` | Replaced by `babycli server start` |
| `scripts/` | `check_domain_boundaries.py` absorbed into `src/babycli/boundaries.py` |
| `seed/` | Logic → `src/babycli/seed/`, data → `src/babycli/resources/seed/` |
| `build/` | Build artifact, add to `.gitignore` |

### Target Layout

```
alembic/
alembic.ini
CLAUDE.md
Dockerfile
docs/
  superpowers/
    specs/
    plans/
mise.toml
pyproject.toml
src/
  babycli/
    __init__.py
    __main__.py
    _utils.py
    boundaries.py         # was scripts/check_domain_boundaries.py
    check.py
    config.py
    danger.py
    db.py
    lint.py
    logs.py
    seed/                 # was top-level seed/
      __init__.py
      categories.py
      config.py
      database.py
      items.py
      regions.py
      users.py
      validators.py
    resources/
      seed/
        data.json
        images/           # seed images
    server.py
    setup.py
    stats.py
    user.py
  babytroc/               # main API (internals unchanged)
    ...
stubs/
tests/
uv.lock
```

## Changes Detail

### 1. Absorb `seed/` into `babycli`

Move `seed/*.py` → `src/babycli/seed/`. Move `seed/data/` → `src/babycli/resources/seed/`.

Update `babycli/db.py` to import from `babycli.seed` instead of top-level `seed`.

Access data files via `importlib.resources`:

```python
from importlib.resources import files

def get_data_file() -> Path:
    return files("babycli.resources.seed").joinpath("data.json")
```

Add to `pyproject.toml` (or let uv_build auto-include — it includes all files in the package by default).

`python -m seed` no longer works. `babycli db seed` is the only entry point.

### 2. Absorb `scripts/check_domain_boundaries.py` into `babycli`

Move script logic to `src/babycli/boundaries.py` as a module with a `check_boundaries(strict: bool) -> list[str]` function.

Update `src/babycli/lint.py`:
- `lint boundaries` calls `check_boundaries()` directly (no subprocess)
- `lint ruff` and `lint mypy` still use subprocess (external tools)

Delete `scripts/` directory.

Update `DOMAINS_ROOT` path in boundaries.py: uses `importlib.resources` or `Path(__file__).parent.parent / "babytroc" / "domains"` — whichever resolves correctly from installed package context.

### 3. Remove `entrypoint.sh`

Delete `entrypoint.sh`.

Update `Dockerfile`:
```dockerfile
ENTRYPOINT ["babycli", "server", "start"]
```

`babycli server start` already runs `alembic upgrade head` + `uvicorn`, matching entrypoint.sh behavior.

### 4. Remove `build/`

Delete `build/` from repo. Add `build/` to `.gitignore`.

### 5. Config files stay at root

No change to: `alembic.ini`, `pyproject.toml`, `mise.toml`, `CLAUDE.md`, `Dockerfile`, `uv.lock`.

### 6. `stubs/` stays at root

Standard convention for mypy type stubs. No change.

### 7. Update `mise.toml`

Remove `[tasks.seed]` — replaced by `babycli db seed`.

Update `[tasks."lint:mypy"]` if mypy paths changed (seed no longer top-level).

### 8. Update `CLAUDE.md`

Reflect new paths and commands. `python -m seed` → `babycli db seed`. Remove references to `scripts/` and `entrypoint.sh`.

## Testing

- All existing tests pass (no logic changes, only file moves + import updates)
- `babycli db seed --help` still works
- `babycli lint boundaries` works without subprocess
- `babycli server start` works (replaces entrypoint.sh)
- `uv run babycli --help` works
- Docker build succeeds

## Success Criteria

- Top-level has only: `alembic/`, `alembic.ini`, `CLAUDE.md`, `Dockerfile`, `docs/`, `mise.toml`, `pyproject.toml`, `src/`, `stubs/`, `tests/`, `uv.lock`
- No `seed/`, `scripts/`, `entrypoint.sh`, `build/` at top level
- All babycli commands functional
- All tests pass
