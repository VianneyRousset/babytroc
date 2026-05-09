# Directory Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean top-level layout by absorbing `seed/`, `scripts/` into babycli, removing `entrypoint.sh` and `build/`, declaring seed data as package resources.

**Architecture:** Move seed logic to `src/babycli/seed/`, seed data to `src/babycli/resources/seed/`, boundary checker to `src/babycli/boundaries.py`. Update all imports and configs. Delete orphaned top-level dirs.

**Tech Stack:** Python 3.13, cyclopts, importlib.resources, uv_build

**Spec:** `docs/superpowers/specs/2026-05-09-directory-restructure-design.md`

---

## File Structure

```
Modified:
  src/babycli/db.py           — update seed imports from babycli.seed
  src/babycli/lint.py          — call boundaries.check_boundaries() directly
  Dockerfile                   — remove entrypoint.sh, use babycli
  mise.toml                    — remove seed task, update mypy/dev
  pyproject.toml               — remove seed from mypy, resources auto-included
  .gitignore                   — add build/

Created:
  src/babycli/boundaries.py    — absorbed from scripts/check_domain_boundaries.py
  src/babycli/seed/__init__.py — absorbed from seed/__main__.py (logic only, no cyclopts App)
  src/babycli/seed/config.py   — from seed/config.py
  src/babycli/seed/database.py — from seed/database.py
  src/babycli/seed/categories.py
  src/babycli/seed/items.py
  src/babycli/seed/regions.py
  src/babycli/seed/users.py
  src/babycli/seed/validators.py
  src/babycli/resources/__init__.py
  src/babycli/resources/seed/  — data.json + images/ moved from seed/data/

Deleted:
  seed/                        — entire directory
  scripts/                     — entire directory
  entrypoint.sh
  build/
```

---

## Task 1: Move seed data to resources

**Files:**
- Create: `src/babycli/resources/__init__.py`
- Move: `seed/data/data.json` → `src/babycli/resources/seed/data.json`
- Move: `seed/data/images/` → `src/babycli/resources/seed/images/`

- [ ] **Step 1: Create resources directory and move data**

```bash
mkdir -p src/babycli/resources/seed
touch src/babycli/resources/__init__.py
touch src/babycli/resources/seed/__init__.py
cp seed/data/data.json src/babycli/resources/seed/data.json
cp -r seed/data/images src/babycli/resources/seed/images
```

- [ ] **Step 2: Verify files exist**

```bash
ls src/babycli/resources/seed/data.json
ls src/babycli/resources/seed/images/
```

Expected: data.json present, images directory with files.

- [ ] **Step 3: Commit**

```bash
git add src/babycli/resources/
git commit -m "chore: copy seed data to babycli resources"
```

---

## Task 2: Move seed logic into babycli

**Files:**
- Create: `src/babycli/seed/__init__.py` (from `seed/__main__.py`, stripped of cyclopts App)
- Create: `src/babycli/seed/config.py`
- Create: `src/babycli/seed/database.py`
- Create: `src/babycli/seed/categories.py`
- Create: `src/babycli/seed/items.py`
- Create: `src/babycli/seed/regions.py`
- Create: `src/babycli/seed/users.py`
- Create: `src/babycli/seed/validators.py`

- [ ] **Step 1: Copy seed modules**

```bash
mkdir -p src/babycli/seed
cp seed/config.py src/babycli/seed/config.py
cp seed/database.py src/babycli/seed/database.py
cp seed/categories.py src/babycli/seed/categories.py
cp seed/items.py src/babycli/seed/items.py
cp seed/regions.py src/babycli/seed/regions.py
cp seed/users.py src/babycli/seed/users.py
cp seed/validators.py src/babycli/seed/validators.py
```

- [ ] **Step 2: Create `src/babycli/seed/__init__.py`**

Strip the cyclopts App from `seed/__main__.py`. Keep only the populate functions and helpers. Update data file paths to use `importlib.resources`. The `__init__.py` exports the populate functions that `babycli/db.py` calls.

```python
# src/babycli/seed/__init__.py
import json
import logging
from importlib.resources import files
from pathlib import Path
from typing import Annotated

from .categories import (
    Category as Category,
    check_categories as _check_categories,
    populate_categories as _populate_categories,
)
from .database import shared_session
from .items import (
    check_items as _check_items,
    populate_items as _populate_items,
)
from .regions import (
    Region,
    check_regions as _check_regions,
    populate_regions as _populate_regions,
)
from .users import (
    User,
    check_users as _check_users,
    populate_users as _populate_users,
)

logger = logging.getLogger("babycli.seed")


def _default_data_file() -> Path:
    return Path(str(files("babycli.resources.seed").joinpath("data.json")))


def _default_images_dir() -> Path:
    return Path(str(files("babycli.resources.seed").joinpath("images")))


def read_regions(file: Path) -> list[Region]:
    with file.open() as f:
        data = json.load(f)
        return [Region.model_validate(reg) for reg in data["regions"]]


def read_categories(file: Path) -> list[Category]:
    with file.open() as f:
        data = json.load(f)
        return [Category.model_validate(cat) for cat in data["categories"]]


def read_users(file: Path) -> list[User]:
    with file.open() as f:
        data = json.load(f)
        return [User.model_validate(reg) for reg in data["users"]]


async def populate_all(
    fp: Path | None = None,
    items_count: int = 50,
    force: bool = False,
) -> None:
    """Populate regions, users and items."""
    if fp is None:
        fp = _default_data_file()

    logger.info("Starting populate all")
    async with shared_session:
        await populate_regions_cmd(fp=fp, force=force)
        await populate_categories_cmd(fp=fp, force=force)
        await populate_users_cmd(fp=fp, force=force)
        await populate_items_cmd(items_count=items_count, force=force)


async def populate_regions_cmd(
    fp: Path | None = None,
    force: bool = False,
) -> None:
    """Populate regions."""
    if fp is None:
        fp = _default_data_file()

    logger.info("Starting populate regions")
    regions = read_regions(fp)
    logger.info("%i regions found in %s", len(regions), fp)

    async with shared_session as db:
        if await _check_regions(db):
            logger.warning("Regions already populated.")
            if not force:
                msg = "Regions already populated."
                raise RuntimeError(msg)
        await _populate_regions(db, regions)


async def populate_categories_cmd(
    fp: Path | None = None,
    force: bool = False,
) -> None:
    """Populate categories."""
    if fp is None:
        fp = _default_data_file()

    logger.info("Starting populate categories")
    categories = read_categories(fp)
    logger.info("%i categories found in %s", len(categories), fp)

    async with shared_session as db:
        if await _check_categories(db):
            logger.warning("Categories already populated.")
            if not force:
                msg = "Categories already populated."
                raise RuntimeError(msg)
        await _populate_categories(db, categories)


async def populate_users_cmd(
    fp: Path | None = None,
    force: bool = False,
) -> None:
    """Populate users."""
    if fp is None:
        fp = _default_data_file()

    logger.info("Starting populate users")
    users = read_users(fp)
    logger.info("%i users found in %s", len(users), fp)

    async with shared_session as db:
        if await _check_users(db):
            logger.warning("Users already populated.")
            if not force:
                msg = "Users already populated."
                raise RuntimeError(msg)
        await _populate_users(db, users)


async def populate_items_cmd(
    items_count: int = 20,
    force: bool = False,
) -> None:
    """Populate items."""
    logger.info("Starting populate items")
    logger.info("%i items will be generated", items_count)

    async with shared_session as db:
        if await _check_items(db):
            logger.warning("Items already populated.")
            if not force:
                msg = "Items already populated."
                raise RuntimeError(msg)
        await _populate_items(
            db=db,
            images_dir=_default_images_dir(),
            count=items_count,
        )
```

- [ ] **Step 3: Update `src/babycli/db.py`**

Replace all `from seed.__main__ import ...` with `from babycli.seed import ...`. Update default data_file paths to use `None` (let seed module resolve via importlib.resources).

```python
# src/babycli/db.py
import sys
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from ._utils import confirm_prompt, console_err, console_ok, run_subprocess
from .danger import require_danger

db_app = App(
    name="db",
    help="Database management (migrations, seed, reset).",
)

seed_app = App(
    name="seed",
    help="Seed database with dev data.",
)

db_app.command(seed_app)


@db_app.command(name="migrate")
def migrate():
    """Run alembic upgrade head."""
    code = run_subprocess(["alembic", "upgrade", "head"])
    if code != 0:
        console_err("Migration failed")
        sys.exit(code)
    console_ok("Migrations applied")


@db_app.command(name="downgrade")
def downgrade(
    revision: Annotated[
        str,
        Parameter(
            help="Target revision (default: -1 for one step back).",
        ),
    ] = "-1",
):
    """Run alembic downgrade."""
    code = run_subprocess(["alembic", "downgrade", revision])
    if code != 0:
        console_err("Downgrade failed")
        sys.exit(code)
    console_ok(f"Downgraded to {revision}")


@db_app.command(name="status")
def status():
    """Show current migration status."""
    run_subprocess(["alembic", "current"])


@db_app.command(name="reset")
def reset(
    danger: Annotated[
        bool,
        Parameter(name="--danger", help="Confirm destructive operation."),
    ] = False,
    with_seed: Annotated[
        bool,
        Parameter(name="--seed", help="Re-seed after reset."),
    ] = False,
):
    """Drop all tables and re-migrate. DESTRUCTIVE."""
    require_danger(danger_flag=danger)
    if not confirm_prompt("This will DROP ALL TABLES. Continue?"):
        print("Aborted.")
        return

    code = run_subprocess(["alembic", "downgrade", "base"])
    if code != 0:
        console_err("Downgrade to base failed")
        sys.exit(code)

    code = run_subprocess(["alembic", "upgrade", "head"])
    if code != 0:
        console_err("Re-migration failed")
        sys.exit(code)

    console_ok("Database reset complete")

    if with_seed:
        import asyncio

        from .seed import populate_all

        asyncio.run(populate_all())
        console_ok("Seed data populated")


@seed_app.command(name="all")
async def seed_all(
    data_file: Annotated[
        Path | None,
        Parameter(
            name="--data-file",
            help="Data file (default: bundled resource).",
        ),
    ] = None,
    items_count: Annotated[
        int,
        Parameter(
            name=["--items-count", "-n"],
            help="Total number of generated items.",
        ),
    ] = 50,
    force: Annotated[
        bool,
        Parameter(
            name=["--force", "-f"],
            help="Force populate even if already populated.",
        ),
    ] = False,
    danger: Annotated[
        bool,
        Parameter(
            name="--danger",
            help=(
                "Confirm destructive operation"
                " (required with --force)."
            ),
        ),
    ] = False,
):
    """Populate all dev data (regions, categories, users, items)."""
    if force:
        require_danger(danger_flag=danger)

    from .seed import populate_all as _populate_all

    await _populate_all(
        fp=data_file, items_count=items_count, force=force,
    )
    console_ok("Seed complete")


@seed_app.command(name="regions")
async def seed_regions(
    data_file: Annotated[
        Path | None,
        Parameter(name="--data-file", help="Data file."),
    ] = None,
    force: Annotated[
        bool,
        Parameter(name=["--force", "-f"], help="Force re-populate."),
    ] = False,
):
    """Seed regions."""
    from .seed import populate_regions_cmd

    await populate_regions_cmd(fp=data_file, force=force)
    console_ok("Regions seeded")


@seed_app.command(name="categories")
async def seed_categories(
    data_file: Annotated[
        Path | None,
        Parameter(name="--data-file", help="Data file."),
    ] = None,
    force: Annotated[
        bool,
        Parameter(name=["--force", "-f"], help="Force re-populate."),
    ] = False,
):
    """Seed categories."""
    from .seed import populate_categories_cmd

    await populate_categories_cmd(fp=data_file, force=force)
    console_ok("Categories seeded")


@seed_app.command(name="users")
async def seed_users(
    data_file: Annotated[
        Path | None,
        Parameter(name="--data-file", help="Data file."),
    ] = None,
    force: Annotated[
        bool,
        Parameter(name=["--force", "-f"], help="Force re-populate."),
    ] = False,
):
    """Seed users."""
    from .seed import populate_users_cmd

    await populate_users_cmd(fp=data_file, force=force)
    console_ok("Users seeded")


@seed_app.command(name="items")
async def seed_items(
    items_count: Annotated[
        int,
        Parameter(
            name=["--items-count", "-n"], help="Number of items.",
        ),
    ] = 20,
    force: Annotated[
        bool,
        Parameter(name=["--force", "-f"], help="Force re-populate."),
    ] = False,
):
    """Seed items."""
    from .seed import populate_items_cmd

    await populate_items_cmd(items_count=items_count, force=force)
    console_ok("Items seeded")
```

- [ ] **Step 4: Verify babycli db seed --help works**

Run: `uv run babycli db seed --help`
Expected: shows all, regions, categories, users, items subcommands

- [ ] **Step 5: Commit**

```bash
git add src/babycli/seed/ src/babycli/db.py
git commit -m "refactor(babycli): absorb seed into babycli with importlib.resources"
```

---

## Task 3: Absorb boundary checker into babycli

**Files:**
- Create: `src/babycli/boundaries.py`
- Modify: `src/babycli/lint.py`

- [ ] **Step 1: Create `src/babycli/boundaries.py`**

Move the logic from `scripts/check_domain_boundaries.py` into a module. Replace hardcoded `DOMAINS_ROOT` path with dynamic resolution relative to `babytroc` package. Export a `check_boundaries(strict: bool) -> list[str]` function and keep `main()` for standalone use.

```python
# src/babycli/boundaries.py
"""Cross-domain write boundary violation checker.

Rule: domains may import and READ (query) any other domain's models freely,
but WRITES (create/update/delete) to another domain must go through events,
not direct service imports.
"""

import ast
import sys
from pathlib import Path

ALLOWED_CROSS_DOMAIN_WRITES: set[tuple[str, str]] = {
    ("auth", "user"),
    ("loan", "item"),
}

WRITE_PREFIXES = (
    "create", "update", "delete", "add", "remove", "send",
    "accept", "reject", "cancel", "upload", "like", "unlike",
    "save", "unsave", "invalidate", "ensure", "insert",
)

READ_PREFIXES = (
    "get", "list", "read", "count", "check",
    "search", "find", "exists",
)


def _get_domains_root() -> Path:
    """Resolve domains root relative to babytroc package."""
    import babytroc

    return Path(babytroc.__file__).parent / "domains"


def get_domain_name(file_path: Path) -> str | None:
    parts = file_path.parts
    try:
        idx = parts.index("domains")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    except ValueError:
        pass
    return None


def is_handler_file(file_path: Path) -> bool:
    return file_path.name == "handlers.py"


def is_write_function(name: str) -> bool:
    lower = name.lower()
    return any(lower.startswith(p) for p in WRITE_PREFIXES)


def is_read_function(name: str) -> bool:
    lower = name.lower()
    return any(lower.startswith(p) for p in READ_PREFIXES)


def extract_imports(
    file_path: Path,
) -> list[tuple[str, list[str], int]]:
    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            names = [
                alias.name for alias in node.names
                if alias.name != "*"
            ]
            imports.append((node.module, names, node.lineno))
    return imports


def _get_target_domain(
    module_path: str, source_domain: str,
) -> str | None:
    if not module_path.startswith("babytroc.domains."):
        return None
    parts = module_path.split(".")
    if len(parts) < 4:
        return None
    target_domain = parts[2]
    if target_domain == source_domain:
        return None
    if "models" in parts:
        return None
    if "services" not in parts:
        return None
    if (source_domain, target_domain) in ALLOWED_CROSS_DOMAIN_WRITES:
        return None
    return target_domain


def check_file(
    file_path: Path, *, strict: bool = False,
) -> list[str]:
    source_domain = get_domain_name(file_path)
    if source_domain is None:
        return []
    if is_handler_file(file_path):
        return []

    violations = []
    for module_path, names, lineno in extract_imports(file_path):
        target_domain = _get_target_domain(
            module_path, source_domain,
        )
        if target_domain is None:
            continue
        for name in names:
            if is_write_function(name):
                violations.append(
                    f"{file_path}:{lineno}: "
                    f"cross-domain write import '{name}' "
                    f"from '{module_path}' "
                    f"({source_domain} → {target_domain}). "
                    f"Use events instead."
                )
            elif strict and not is_read_function(name):
                violations.append(
                    f"{file_path}:{lineno}: "
                    f"ambiguous cross-domain import '{name}' "
                    f"from '{module_path}' "
                    f"({source_domain} → {target_domain}). "
                    f"Consider if this should be an event."
                )
    return violations


def check_boundaries(*, strict: bool = False) -> list[str]:
    """Run boundary check, return list of violation strings."""
    domains_root = _get_domains_root()
    if not domains_root.exists():
        return [f"Error: {domains_root} not found."]

    all_violations = []
    for py_file in sorted(domains_root.rglob("*.py")):
        if (
            "services" not in py_file.parts
            and "handlers" not in py_file.name
        ):
            continue
        all_violations.extend(check_file(py_file, strict=strict))
    return all_violations
```

- [ ] **Step 2: Update `src/babycli/lint.py`**

Replace subprocess call for boundaries with direct function call. Keep subprocess for ruff and mypy (external tools). Remove `seed` from mypy paths.

```python
# src/babycli/lint.py
import sys
from typing import Annotated

from cyclopts import App, Parameter

from ._utils import console_err, console_ok, run_subprocess

lint_app = App(
    name="lint",
    help="Run code quality checks.",
)


@lint_app.command(name="ruff")
def lint_ruff():
    """Run ruff linter."""
    code = run_subprocess(["ruff", "check", "."])
    if code == 0:
        console_ok("ruff — no issues")
    else:
        console_err("ruff — issues found")
    sys.exit(code)


@lint_app.command(name="mypy")
def lint_mypy():
    """Run mypy type checker."""
    code = run_subprocess(["mypy", "stubs", "src", "tests"])
    if code == 0:
        console_ok("mypy — no issues")
    else:
        console_err("mypy — issues found")
    sys.exit(code)


@lint_app.command(name="boundaries")
def lint_boundaries(
    strict: Annotated[
        bool,
        Parameter(
            name="--strict",
            help="Also flag ambiguous cross-domain imports.",
        ),
    ] = False,
):
    """Run domain boundary violation check."""
    from .boundaries import check_boundaries

    violations = check_boundaries(strict=strict)
    if violations:
        console_err(
            f"Found {len(violations)} boundary violation(s):"
        )
        for v in violations:
            print(f"  {v}")
        print()
        console_err(
            "Fix: move cross-domain write calls to event handlers"
        )
        sys.exit(1)
    else:
        console_ok("boundaries — no violations")


@lint_app.default
def lint_all():
    """Run all linters (ruff + mypy + boundaries)."""
    failed = False

    code = run_subprocess(["ruff", "check", "."])
    if code == 0:
        console_ok("ruff — no issues")
    else:
        console_err("ruff — issues found")
        failed = True

    code = run_subprocess(["mypy", "stubs", "src", "tests"])
    if code == 0:
        console_ok("mypy — no issues")
    else:
        console_err("mypy — issues found")
        failed = True

    from .boundaries import check_boundaries

    violations = check_boundaries()
    if not violations:
        console_ok("boundaries — no violations")
    else:
        console_err(
            f"boundaries — {len(violations)} violation(s) found"
        )
        for v in violations:
            print(f"  {v}")
        failed = True

    if failed:
        sys.exit(1)
```

- [ ] **Step 3: Verify**

Run: `uv run babycli lint --help`
Expected: shows ruff, mypy, boundaries

- [ ] **Step 4: Commit**

```bash
git add src/babycli/boundaries.py src/babycli/lint.py
git commit -m "refactor(babycli): absorb boundary checker, remove subprocess"
```

---

## Task 4: Update Dockerfile, remove entrypoint.sh

**Files:**
- Modify: `Dockerfile`
- Delete: `entrypoint.sh`

- [ ] **Step 1: Update Dockerfile**

```dockerfile
FROM python:3-alpine

RUN apk update
RUN apk add uv git bash

# to build in uv sync
RUN apk add gcc python3-dev musl-dev linux-headers

# set the working directory
WORKDIR /usr/src/api

# install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --no-group dev

# Expose the port the app runs on
EXPOSE 8080

COPY src ./src
COPY alembic.ini .
COPY alembic ./alembic

# Define entrypoint
ENTRYPOINT ["uv", "run", "babycli", "server", "start"]
```

- [ ] **Step 2: Delete entrypoint.sh**

```bash
git rm entrypoint.sh
```

- [ ] **Step 3: Commit**

```bash
git add Dockerfile
git commit -m "refactor: replace entrypoint.sh with babycli server start"
```

---

## Task 5: Update mise.toml and cleanup

**Files:**
- Modify: `mise.toml`
- Modify: `.gitignore` (create if needed)

- [ ] **Step 1: Update mise.toml**

```toml
[env]
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DATABASE = "babytroc"
POSTGRES_USER = "babytroc"
_.file = ".env.yaml"
_.python.venv = { path = ".venv", create = true }

[tools]
python = { version = "3.13", virtualenv = ".venv" }
ruff = "latest"
uv = "latest"

[tasks."deps:mypy"]
description = "Install mypy linter"
run = "uv pip install mypy"

[tasks.deps]
description = "Install dependencies"
run = "uv sync"

[tasks.deps-dev]
description = "Install dev dependencies"
run = "uv sync --group dev"

[tasks.dev]
description = "Run the application"
depends = ["deps", "deps-dev", "prepare"]
run = "uv run babycli server start"

[tasks.prepare]
description = "Prepare database"
depends = ["deps"]
run = "alembic upgrade head"

[tasks."lint:ruff"]
description = "Lint - ruff pass"
depends = ["deps", "deps-dev"]
run = "ruff check ."

[tasks."lint:mypy"]
description = "Lint - mypy pass"
depends = ["deps", "deps-dev"]
run = "mypy stubs src tests"

[tasks.lint]
description = "Lint the code"
depends = ["lint:*"]

[tasks.ipython]
description = "Run ipython"
run = "ipython"

[tasks.test]
description = "Test the code"
depends = ["deps", "deps-dev"]
run = "pytest -n logical --dist loadscope --maxfail=1"

[tasks.build]
description = "Build docker image"
run = "docker build . --tag=vianneyrousset/babytroc-api"

[tasks.clear-mypy-cache]
description = "Clear mypy cache"
run = "rm -rf `find -iname '.mypy_cache'`"

[tasks.babycli]
description = "Run babycli operations CLI"
depends = ["deps", "deps-dev"]
run = "uv run babycli"
```

Changes from current:
- `[tasks.dev]` run → `uv run babycli server start` (was `./entrypoint.sh`)
- `[tasks.seed]` removed entirely
- `[tasks."lint:mypy"]` run → `mypy stubs src tests` (removed `seed`)

- [ ] **Step 2: Add build/ to .gitignore**

Create or append to `.gitignore`:

```
build/
```

- [ ] **Step 3: Remove build/ and delete old directories**

```bash
git rm -rf build/ 2>/dev/null || rm -rf build/
git rm -rf seed/
git rm -rf scripts/
```

- [ ] **Step 4: Commit**

```bash
git add mise.toml .gitignore
git add -A  # stages all deletions
git commit -m "chore: remove seed/, scripts/, build/, update mise.toml"
```

---

## Task 6: Verify and run tests

**Files:** none modified — verification only

- [ ] **Step 1: Verify CLI works**

Run: `uv run babycli --help`
Expected: all 10 command groups listed

Run: `uv run babycli db seed --help`
Expected: shows all, regions, categories, users, items

Run: `uv run babycli lint --help`
Expected: shows ruff, mypy, boundaries

- [ ] **Step 2: Verify top-level is clean**

```bash
ls -1
```

Expected only: `alembic/`, `alembic.ini`, `CLAUDE.md`, `Dockerfile`, `docs/`, `mise.toml`, `pyproject.toml`, `src/`, `stubs/`, `tests/`, `uv.lock`, `.gitignore`

No `seed/`, `scripts/`, `entrypoint.sh`, `build/`.

- [ ] **Step 3: Run babycli tests**

Run: `pytest tests/babycli/ -v`
Expected: all 28 tests pass

- [ ] **Step 4: Run ruff on babycli**

Run: `ruff check src/babycli/`
Expected: no errors (fix any that appear)

- [ ] **Step 5: Run broader tests**

Run: `pytest tests/ -q --maxfail=3`
Expected: tests pass (same flaky websocket test may fail — that's pre-existing)

- [ ] **Step 6: Commit any fixes**

```bash
git add -u
git commit -m "fix: lint and test fixes from directory restructure"
```
