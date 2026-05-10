# Shared DB Templates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single `tests/fixtures/database.py` primary template with a 13-node pg template chain organized as per-domain seed modules + cross-cutting infrastructure, where each test class declares its template via `@pytest.mark.db_template("…")` and each method gets its own clone.

**Architecture:** Templates form a tree built once per xdist worker via chained `CREATE DATABASE … TEMPLATE`. Test classes pick a node via marker; per-method `database` fixture clones from that node. Heavy class-scoped fixtures (`many_items`, `alice_many_loans`, etc.) become SELECT-only fixtures backed by data that already lives in the chosen template.

**Tech Stack:** Python 3.13, pytest-asyncio (auto), pytest-xdist, SQLAlchemy async + asyncpg, alembic. Spec: `docs/superpowers/specs/2026-05-10-shared-db-templates-design.md`.

---

## Worktree

This work spans many test files and is best done in a worktree:

```bash
git worktree add ../babytroc-api-templates -b refactor/shared-db-templates
cd ../babytroc-api-templates/api
```

If you choose to work in-place, ensure no other refactor is mid-flight.

## Final file structure

```
tests/fixtures/database/
├── __init__.py                      re-exports public names; pytest_plugins entries
├── infrastructure/
│   ├── __init__.py
│   ├── admin.py                     create_database, drop_database, set_datallowconn
│   ├── chain.py                     TemplateSpec, build_chain
│   ├── lifecycle.py                 primary_databases, database, database_sessionmaker
│   ├── marker.py                    db_template marker reader
│   └── registry.py                  TEMPLATES = {…}
└── seeds/
    ├── __init__.py
    ├── region.py                    seed_reference_regions
    ├── category.py                  seed_reference_categories,
    │                                seed_alice_items_with_categories
    ├── user.py                      seed_baseline_users, seed_many_users
    ├── image.py                     seed_baseline_images
    ├── item.py                      seed_baseline_items, seed_many_items,
    │                                seed_alice_many_items, seed_french_named_items
    ├── loan.py                      seed_many_loan_requests_for_alice_items,
    │                                seed_alice_many_loans,
    │                                seed_alice_special_item_loan_requests
    └── chat.py                      seed_alice_many_chats
```

Deleted at end:

- `tests/fixtures/database.py`
- `tests/item/conftest.py`
- `tests/loan/conftest.py`
- `tests/chat_read/conftest.py`

Modified:

- `tests/conftest.py` — `pytest_plugins` updated, `db_template` marker registered
- `pyproject.toml` — `[tool.pytest.ini_options].markers` adds `db_template`
- `tests/fixtures/items.py`, `tests/fixtures/loans.py`, `tests/fixtures/users.py`, `tests/fixtures/categories.py`, `tests/fixtures/chat.py` — class-scoped builders become function-scoped SELECT fixtures
- `tests/item/test_*.py`, `tests/loan/test_*.py`, `tests/chat_read/test_chat_read.py` — class-level `@pytest.mark.db_template("…")` markers

---

# PHASE 1 — Infrastructure + 3-node chain (`bare`, `reference`, `baseline`)

End state: new package structure exists; default template is `baseline` and matches today's `_seed_template` byte-for-byte; old `tests/fixtures/database.py` deleted; full test suite green.

## Task 1.1: Scaffold the package

**Files:**
- Create: `tests/fixtures/database/__init__.py`
- Create: `tests/fixtures/database/infrastructure/__init__.py`
- Create: `tests/fixtures/database/seeds/__init__.py`

- [ ] **Step 1: Create `tests/fixtures/database/__init__.py`** (empty file — package marker; public names will be re-exported in Task 1.7)

```python
```

- [ ] **Step 2: Create `tests/fixtures/database/infrastructure/__init__.py`**

```python
```

- [ ] **Step 3: Create `tests/fixtures/database/seeds/__init__.py`**

```python
```

- [ ] **Step 4: Verify package imports work**

Run: `python -c "import tests.fixtures.database; import tests.fixtures.database.infrastructure; import tests.fixtures.database.seeds"` from the project root with `PYTHONPATH=src:.`

Expected: no output, exit 0.

## Task 1.2: PostgreSQL admin helpers

Extract `create_database`, `drop_database`, and the in-progress `_set_datallowconn` from `tests/fixtures/database.py` into a focused infrastructure module. Add a helper that disposes an engine after running a callable against it (used by chain build to ensure no connections survive seed steps).

**Files:**
- Create: `tests/fixtures/database/infrastructure/admin.py`

- [ ] **Step 1: Create `tests/fixtures/database/infrastructure/admin.py`**

```python
"""PostgreSQL admin helpers — CREATE/DROP DATABASE, ALTER ALLOW_CONNECTIONS."""

from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import TypeVar

from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

T = TypeVar("T")


def _admin_url(url: URL) -> URL:
    return url._replace(database="postgres")


async def create_database(
    url: URL,
    *,
    encoding: str = "utf8",
    template: str | None = None,
) -> None:
    """`CREATE DATABASE url.database TEMPLATE template`. Defaults to template1."""
    database = url.database
    if database is None:
        msg = "url.database must be set"
        raise ValueError(msg)

    engine = create_async_engine(
        _admin_url(url), isolation_level="AUTOCOMMIT", poolclass=NullPool,
    )
    try:
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    f'CREATE DATABASE "{database}" '
                    f"ENCODING '{encoding}' "
                    f'TEMPLATE "{template or "template1"}"'
                )
            )
    finally:
        await engine.dispose()


async def drop_database(url: URL) -> None:
    """`DROP DATABASE url.database`."""
    database = url.database
    if database is None:
        msg = "url.database must be set"
        raise ValueError(msg)

    engine = create_async_engine(
        _admin_url(url), isolation_level="AUTOCOMMIT", poolclass=NullPool,
    )
    try:
        async with engine.begin() as conn:
            await conn.execute(text(f'DROP DATABASE "{database}"'))
    finally:
        await engine.dispose()


async def set_datallowconn(url: URL, *, allow: bool) -> None:
    """ALTER DATABASE WITH ALLOW_CONNECTIONS = …."""
    database = url.database
    if database is None:
        msg = "url.database must be set"
        raise ValueError(msg)

    engine = create_async_engine(
        _admin_url(url), isolation_level="AUTOCOMMIT", poolclass=NullPool,
    )
    try:
        async with engine.begin() as conn:
            val = "true" if allow else "false"
            await conn.execute(
                text(f'ALTER DATABASE "{database}" WITH ALLOW_CONNECTIONS = {val}')
            )
    finally:
        await engine.dispose()


@asynccontextmanager
async def session_against(url: URL):
    """Open a session against `url`, yield it inside a transaction, dispose engine.

    Critical: dispose runs in finally so no connections survive — required
    before any downstream `CREATE DATABASE … TEMPLATE` of this URL.
    """
    engine = create_async_engine(url=url, echo=False, poolclass=NullPool)
    maker = async_sessionmaker(bind=engine)
    try:
        async with maker.begin() as session:
            yield session
    finally:
        await engine.dispose()


async def run_against(
    url: URL,
    fn: Callable[[AsyncSession], Awaitable[T]],
) -> T:
    """Run `fn(session)` inside a transaction against `url` and dispose engine."""
    async with session_against(url) as session:
        return await fn(session)
```

- [ ] **Step 2: Verify imports**

Run: `python -c "from tests.fixtures.database.infrastructure.admin import create_database, drop_database, set_datallowconn, session_against, run_against"` (from project root, `PYTHONPATH=src`).

Expected: no output.

## Task 1.3: Domain seed modules — region, category, user, image (Phase-1 subset)

Extract the seed body of `_seed_template` in `tests/fixtures/database.py` (lines 46-197) into per-domain modules. Phase 1 includes only the seeds needed by `tpl_reference` and `tpl_baseline`.

**Files:**
- Create: `tests/fixtures/database/seeds/region.py`
- Create: `tests/fixtures/database/seeds/category.py`
- Create: `tests/fixtures/database/seeds/user.py`
- Create: `tests/fixtures/database/seeds/image.py`

- [ ] **Step 1: Create `tests/fixtures/database/seeds/region.py`**

```python
"""Reference region seed."""

from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.region.schemas.create import RegionCreate
from babytroc.domains.region.services import create_region
from tests.fixtures.database.infrastructure.chain import SeedContext


async def seed_reference_regions(db: AsyncSession, ctx: SeedContext) -> None:
    """Insert the two canonical test regions."""
    del ctx  # not used by this seed
    await create_region(db=db, region_create=RegionCreate(id=1, name="region1"))
    await create_region(db=db, region_create=RegionCreate(id=2, name="region2"))
```

- [ ] **Step 2: Create `tests/fixtures/database/seeds/category.py`** (Phase 1 has only the reference seed; `seed_alice_items_with_categories` lands in Phase 3)

```python
"""Reference category seed."""

from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.category.schemas.create import CategoryCreate
from babytroc.domains.category.services import create_many_categories
from tests.fixtures.database.infrastructure.chain import SeedContext

_PARENTS = [
    CategoryCreate(slug="clothing", name="Vêtements"),
    CategoryCreate(slug="toys", name="Jouets"),
    CategoryCreate(slug="gear", name="Équipement"),
]

_CHILDREN = [
    CategoryCreate(slug="clothing-bodysuits", name="Bodies", parent_slug="clothing"),
    CategoryCreate(slug="clothing-sleepwear", name="Pyjamas", parent_slug="clothing"),
    CategoryCreate(slug="clothing-outerwear", name="Manteaux", parent_slug="clothing"),
    CategoryCreate(slug="clothing-accessories", name="Accessoires", parent_slug="clothing"),
    CategoryCreate(slug="toys-bath", name="Jouets de bain", parent_slug="toys"),
    CategoryCreate(slug="toys-soft", name="Peluches", parent_slug="toys"),
    CategoryCreate(slug="toys-educational", name="Jouets éducatifs", parent_slug="toys"),
    CategoryCreate(slug="gear-strollers", name="Poussettes", parent_slug="gear"),
    CategoryCreate(slug="gear-car-seats", name="Sièges auto", parent_slug="gear"),
    CategoryCreate(slug="gear-carriers", name="Porte-bébés", parent_slug="gear"),
]


async def seed_reference_categories(db: AsyncSession, ctx: SeedContext) -> None:
    """Insert the canonical 3 parent + 10 child categories."""
    del ctx
    await create_many_categories(db=db, category_creates=_PARENTS)
    await create_many_categories(db=db, category_creates=_CHILDREN)
```

- [ ] **Step 3: Create `tests/fixtures/database/seeds/user.py`** (Phase 1 has only baseline; `seed_many_users` lands in Phase 4)

```python
"""User seeds — baseline triple and bulk many_users."""

from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.user.schemas.create import UserCreate
from babytroc.domains.user.services import create_many_users_without_validation
from tests.fixtures.database.infrastructure.chain import SeedContext

_BASELINE_USERS = [
    UserCreate(name="alice", email="alice@babytroc.ch", password="password-Alice-42"),
    UserCreate(name="bob", email="bob@babytroc.ch", password="password-Bob-42"),
    UserCreate(name="carol", email="carol@babytroc.ch", password="password-Carol-42"),
]


async def seed_baseline_users(db: AsyncSession, ctx: SeedContext) -> None:
    """Insert alice, bob, carol with `validated=True`."""
    del ctx
    await create_many_users_without_validation(
        db=db,
        user_creates=_BASELINE_USERS,
        validated=True,
    )
```

- [ ] **Step 4: Create `tests/fixtures/database/seeds/image.py`** (PBM uploads — same bytes as today's `_seed_template`)

```python
"""Baseline image seed — Alice and Bob's PBM item images."""

from io import BytesIO

from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.image.services import upload_image
from babytroc.domains.user.services import get_user_by_email_private
from tests.fixtures.database.infrastructure.chain import SeedContext

_ALICE_ITEMS_IMG = b"P1\n3 3\n101\n101\n010"
_ALICE_NEW_ITEM_IMG = b"P1\n3 3\n000\n111\n000"
_ALICE_SPECIAL_ITEM_IMG = b"P1\n3 3\n101\n111\n010"
_BOB_ITEMS_IMG = b"P1\n3 3\n101\n101\n010"


async def seed_baseline_images(db: AsyncSession, ctx: SeedContext) -> None:
    """Upload 7 PBM images: 1 alice_items, 3 alice_new_item, 2 alice_special_item, 1 bob_items.

    Order matters — `alice_items_image`, `alice_new_item_images`,
    `alice_special_item_images`, `bob_items_image` fixtures select by
    `ItemImage.name` ordering.
    """
    config = ctx.config
    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")

    await upload_image(config=config, db=db, owner_id=alice.id, fp=BytesIO(_ALICE_ITEMS_IMG))

    for _ in range(3):
        await upload_image(
            config=config, db=db, owner_id=alice.id, fp=BytesIO(_ALICE_NEW_ITEM_IMG),
        )

    for _ in range(2):
        await upload_image(
            config=config, db=db, owner_id=alice.id, fp=BytesIO(_ALICE_SPECIAL_ITEM_IMG),
        )

    await upload_image(config=config, db=db, owner_id=bob.id, fp=BytesIO(_BOB_ITEMS_IMG))
```

- [ ] **Step 5: Verify imports**

Run: `python -c "from tests.fixtures.database.seeds.region import seed_reference_regions; from tests.fixtures.database.seeds.category import seed_reference_categories; from tests.fixtures.database.seeds.user import seed_baseline_users; from tests.fixtures.database.seeds.image import seed_baseline_images"` (PYTHONPATH=src).

Expected: no output.

## Task 1.4: TemplateSpec + chain build engine

Define the data model for a template node and the function that builds the whole chain in topological order, with each step disposing its engine before the next clone.

**Files:**
- Create: `tests/fixtures/database/infrastructure/chain.py`

- [ ] **Step 1: Create `tests/fixtures/database/infrastructure/chain.py`**

```python
"""Template chain build engine.

A `TemplateSpec` declares one named template: its parent (or None for the
root), the alembic-applied flag, and a list of seed callables. `build_chain`
walks the registry in topological order, creating each template via
`CREATE DATABASE … TEMPLATE`, optionally running alembic, and running the
seed callables inside a single transaction. Each step disposes its engine
so the next `CREATE DATABASE TEMPLATE` of this DB has no active connections.

Seed signature: `async def seed(db: AsyncSession, ctx: SeedContext) -> None`.
Every seed receives the same `SeedContext` object — fields it doesn't need
are simply ignored. This avoids per-template kwargs plumbing.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.infrastructure.config import Config
from tests.fixtures.database.infrastructure.admin import (
    create_database,
    drop_database,
    run_against,
)


@dataclass(frozen=True)
class SeedContext:
    """Cross-cutting context every seed receives."""

    config: Config


SeedFn = Callable[[AsyncSession, SeedContext], Awaitable[None]]


@dataclass(frozen=True)
class TemplateSpec:
    """One template node in the chain."""

    name: str
    parent: str | None
    seeds: tuple[SeedFn, ...] = ()
    apply_alembic: bool = False


def _topo_sort(specs: dict[str, TemplateSpec]) -> list[str]:
    visited: set[str] = set()
    order: list[str] = []

    def visit(name: str, stack: tuple[str, ...]) -> None:
        if name in visited:
            return
        if name in stack:
            cycle = " → ".join((*stack, name))
            msg = f"Template chain cycle: {cycle}"
            raise ValueError(msg)
        spec = specs[name]
        if spec.parent is not None:
            visit(spec.parent, (*stack, name))
        visited.add(name)
        order.append(name)

    for n in specs:
        visit(n, ())
    return order


def _alembic_upgrade_head(url: URL) -> None:
    project_root = Path(__file__).resolve().parents[4]
    cfg = AlembicConfig(project_root / "alembic.ini")
    cfg.set_main_option("script_location", str(project_root / "alembic"))
    cfg.set_main_option("sqlalchemy.url", url.render_as_string(hide_password=False))
    command.upgrade(cfg, "head")


def _make_url(base: URL, *, name: str, worker_id: str) -> URL:
    return base._replace(database=f"tpl-{name}-{worker_id}-{uuid4().hex[:8]}")


async def build_chain(
    *,
    base_url: URL,
    worker_id: str,
    specs: dict[str, TemplateSpec],
    ctx: SeedContext,
) -> dict[str, URL]:
    """Build every template in `specs` in topological order. Returns name → URL."""
    order = _topo_sort(specs)
    urls: dict[str, URL] = {}

    for name in order:
        spec = specs[name]
        url = _make_url(base_url, name=name, worker_id=worker_id)
        parent_db = urls[spec.parent].database if spec.parent else None
        await create_database(url, template=parent_db)

        if spec.apply_alembic:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, partial(_alembic_upgrade_head, url))

        if spec.seeds:
            async def _run_all(session, _seeds=spec.seeds, _ctx=ctx):
                for seed in _seeds:
                    await seed(session, _ctx)
            await run_against(url, _run_all)

        urls[name] = url

    return urls


async def teardown_chain(urls: dict[str, URL]) -> None:
    """Drop all chain DBs in reverse order. Errors on individual drops are swallowed."""
    for url in reversed(list(urls.values())):
        try:
            await drop_database(url)
        except Exception:  # noqa: BLE001, S110
            pass
```

- [ ] **Step 2: Verify imports**

Run: `python -c "from tests.fixtures.database.infrastructure.chain import TemplateSpec, build_chain, teardown_chain"` (PYTHONPATH=src).

Expected: no output.

## Task 1.5: Registry — Phase 1 nodes only

Initial registry has only `bare`, `reference`, `baseline`. Later phases append entries.

**Files:**
- Create: `tests/fixtures/database/infrastructure/registry.py`

- [ ] **Step 1: Create `tests/fixtures/database/infrastructure/registry.py`**

```python
"""Template registry — single source of truth for the chain.

Append entries here as later phases add templates. The chain is built by
`build_chain(specs=TEMPLATES)`.
"""

from tests.fixtures.database.infrastructure.chain import TemplateSpec
from tests.fixtures.database.seeds.category import seed_reference_categories
from tests.fixtures.database.seeds.image import seed_baseline_images
from tests.fixtures.database.seeds.region import seed_reference_regions
from tests.fixtures.database.seeds.user import seed_baseline_users

TEMPLATES: dict[str, TemplateSpec] = {
    "bare": TemplateSpec(
        name="bare",
        parent=None,
        apply_alembic=True,
    ),
    "reference": TemplateSpec(
        name="reference",
        parent="bare",
        seeds=(seed_reference_regions, seed_reference_categories),
    ),
    "baseline": TemplateSpec(
        name="baseline",
        parent="reference",
        seeds=(seed_baseline_users, seed_baseline_images),
    ),
}

DEFAULT_TEMPLATE = "baseline"
```

- [ ] **Step 2: Verify import + topological sort**

Run: `python -c "from tests.fixtures.database.infrastructure.registry import TEMPLATES; from tests.fixtures.database.infrastructure.chain import _topo_sort; print(_topo_sort(TEMPLATES))"` (PYTHONPATH=src).

Expected: `['bare', 'reference', 'baseline']`.

## Task 1.6: Marker reader

The `db_template` marker is the test-side API. The reader looks up the closest marker on the test function/class, defaulting to `DEFAULT_TEMPLATE`.

**Files:**
- Create: `tests/fixtures/database/infrastructure/marker.py`

- [ ] **Step 1: Create `tests/fixtures/database/infrastructure/marker.py`**

```python
"""@pytest.mark.db_template marker reader."""

import pytest

from tests.fixtures.database.infrastructure.registry import (
    DEFAULT_TEMPLATE,
    TEMPLATES,
)

MARKER_NAME = "db_template"


def get_template_name(request: pytest.FixtureRequest) -> str:
    """Return the template name declared by `@pytest.mark.db_template("…")`.

    Looks at the closest marker (function → class → module). Defaults to
    DEFAULT_TEMPLATE if no marker is set.
    """
    marker = request.node.get_closest_marker(MARKER_NAME)
    if marker is None:
        return DEFAULT_TEMPLATE

    if not marker.args:
        msg = f"@pytest.mark.{MARKER_NAME}(...) requires a template name argument"
        raise ValueError(msg)

    name = marker.args[0]
    if name not in TEMPLATES:
        valid = ", ".join(sorted(TEMPLATES))
        msg = f"Unknown db_template {name!r}. Valid: {valid}"
        raise ValueError(msg)

    return name
```

- [ ] **Step 2: Verify import**

Run: `python -c "from tests.fixtures.database.infrastructure.marker import get_template_name, MARKER_NAME"` (PYTHONPATH=src).

Expected: no output.

## Task 1.7: Lifecycle fixtures

The session-scoped `primary_databases` builds the chain. The function-scoped `database` clones from the marker-selected node. `database_sessionmaker` swaps the app session maker.

**Files:**
- Create: `tests/fixtures/database/infrastructure/lifecycle.py`
- Modify: `tests/fixtures/database/__init__.py` — re-export `pytest_plugins` glue

- [ ] **Step 1: Create `tests/fixtures/database/infrastructure/lifecycle.py`**

```python
"""Pytest fixtures for the template chain and per-test DB clones."""

from __future__ import annotations

import os
import warnings
from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy import URL
from sqlalchemy.exc import SAWarning
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from babytroc.infrastructure.config import Config, S3Config
from babytroc.infrastructure.database import init_db_session_dependency
from tests.fixtures.database.infrastructure.admin import (
    create_database,
    drop_database,
)
from tests.fixtures.database.infrastructure.chain import (
    SeedContext,
    build_chain,
    teardown_chain,
)
from tests.fixtures.database.infrastructure.marker import get_template_name
from tests.fixtures.database.infrastructure.registry import TEMPLATES

# match prior global behavior
warnings.simplefilter("error", SAWarning)


def _pg_base_url() -> URL:
    return URL.create(
        drivername="postgresql+asyncpg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        database="postgres",
    )


def _seed_config() -> Config:
    """Config used during chain seed (notably for image upload to mocked S3)."""
    return Config.from_env(
        s3=S3Config(
            endpoint_url="http://localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket="test-bucket",
            public_url="http://localhost:9000/test-bucket",
        ),
    )


@pytest.fixture(scope="session")
async def primary_databases(worker_id: str) -> AsyncGenerator[dict[str, URL]]:
    """Build the full template chain once per xdist worker. Yields name → URL."""
    base = _pg_base_url()
    ctx = SeedContext(config=_seed_config())

    urls = await build_chain(
        base_url=base,
        worker_id=worker_id,
        specs=TEMPLATES,
        ctx=ctx,
    )
    try:
        yield urls
    finally:
        await teardown_chain(urls)


@pytest.fixture(scope="session")
async def primary_database(primary_databases: dict[str, URL]) -> URL:
    """Compatibility shim — the previous "primary_database" was the baseline.

    Keeps `tests/fixtures/app.py::app_config` working until that fixture is
    updated separately. Returns the URL of `tpl_baseline`.
    """
    return primary_databases["baseline"]


@pytest.fixture(scope="function")
async def database(
    primary_databases: dict[str, URL],
    request: pytest.FixtureRequest,
    testrun_uid: str,
) -> AsyncGenerator[URL]:
    """Per-test DB cloned from the marker-selected template."""
    template_name = get_template_name(request)
    template_url = primary_databases[template_name]

    name = f"test-{uuid4()}-{testrun_uid}"
    url = template_url._replace(database=name)
    await create_database(url, template=template_url.database)
    try:
        yield url
    finally:
        await drop_database(url)


@pytest.fixture(scope="function")
async def database_sessionmaker(
    database: URL,
) -> AsyncGenerator[async_sessionmaker]:
    """Sessionmaker against the per-test DB; swaps it into the FastAPI app."""
    engine = create_async_engine(url=database, echo=False, poolclass=NullPool)
    maker = async_sessionmaker(bind=engine)
    init_db_session_dependency(maker)
    try:
        yield maker
    finally:
        await engine.dispose()
```

- [ ] **Step 2: Wire the package — update `tests/fixtures/database/__init__.py`**

```python
"""Public surface — pytest auto-discovers fixtures via pytest_plugins.

Fixtures live in `infrastructure.lifecycle`; importing this module is enough
because `tests/conftest.py::pytest_plugins` references this package.
"""

from tests.fixtures.database.infrastructure.lifecycle import (  # noqa: F401
    database,
    database_sessionmaker,
    primary_database,
    primary_databases,
)
```

- [ ] **Step 3: Verify imports**

Run: `python -c "from tests.fixtures.database import database, database_sessionmaker, primary_database, primary_databases"` (PYTHONPATH=src).

Expected: no output.

## Task 1.8: Register the marker and switch `tests/conftest.py`

**Files:**
- Modify: `pyproject.toml` — register `db_template` marker
- Modify: `tests/conftest.py` — replace `tests.fixtures.database` plugin entry with `tests.fixtures.database` (the new package — same string, but now resolves to a package)

- [ ] **Step 1: Add `db_template` to pytest markers in `pyproject.toml`**

Find the existing `[tool.pytest.ini_options]` block and add a `markers` key:

```toml
[tool.pytest.ini_options]
timeout = 10
timeout_func_only = true
pythonpath = "src"
addopts = "-vv -n logical --dist loadfile --maxfail=1 --reruns 5 --reruns-delay 1"
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
asyncio_default_test_loop_scope = "session"
log_level = "ERROR"
markers = [
    "db_template(name): per-class template selector for the test DB clone",
]
```

- [ ] **Step 2: Confirm `tests/conftest.py` plugin path still works**

The existing entry `"tests.fixtures.database"` continues to resolve — first to the new package's `__init__.py` (which imports the lifecycle fixtures). No edit needed yet.

- [ ] **Step 3: Smoke-run a non-DB test**

Run: `pytest tests/test_image_variants.py -v --no-header -p no:cacheprovider` (timeout 30s).

Expected: PASS — these tests don't touch the DB at all but exercise the import chain.

## Task 1.9: Delete old `tests/fixtures/database.py`

The new package supersedes it. Plugin path resolves to the package because Python imports the package over a sibling module of the same name only when both exist on sys.path; since we deleted the module, the package wins cleanly.

- [ ] **Step 1: Delete the file**

```bash
git rm tests/fixtures/database.py
```

- [ ] **Step 2: Run the full test suite**

Run: `mise run test`

Expected: PASS — same number of tests, same outcomes as before. The 3 chain templates (`bare`, `reference`, `baseline`) get built per worker; `baseline` is byte-equivalent to the old `_seed_template`.

If a fixture in `tests/fixtures/regions.py` or `tests/fixtures/categories.py` or `tests/fixtures/users.py` fails because it relied on an internal import from `tests.fixtures.database`, fix the import at the breakage site.

- [ ] **Step 3: Commit Phase 1**

```bash
git add tests/fixtures/database pyproject.toml
git rm tests/fixtures/database.py
git commit -m "$(cat <<'EOF'
test(db): split seed into 3-node chain (bare/reference/baseline)

Replaces tests/fixtures/database.py with a tests/fixtures/database/
package: infrastructure/ for pg admin + chain engine + lifecycle fixtures
+ marker reader, seeds/ for per-domain seed functions. Registers the
db_template pytest marker. The "baseline" template is byte-equivalent to
the previous _seed_template so all existing tests pass unchanged.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# PHASE 2 — `tpl_baseline_items`

End state: `alice_items`, `bob_items`, `alice_new_item`, `alice_special_item` move from function-scoped builders to function-scoped SELECT fixtures backed by `tpl_baseline_items`. Default template switches to `baseline_items` so untouched tests keep working.

## Task 2.1: `seeds/item.py::seed_baseline_items`

Move the body of today's `alice_items`, `bob_items`, `alice_new_item`, `alice_special_item` fixtures into one seed function. The seed creates the same items the fixtures create, in the same order, so SELECT-by-`id` returns identical objects.

**Files:**
- Create: `tests/fixtures/database/seeds/item.py`

- [ ] **Step 1: Create `tests/fixtures/database/seeds/item.py`** (Phase 2 only adds `seed_baseline_items`; `seed_many_items`, `seed_alice_many_items`, `seed_french_named_items` arrive in Phase 3)

```python
"""Item seeds — baseline items per Alice/Bob; bulk variants in Phase 3."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.image.schemas.read import ItemImageRead
from babytroc.domains.item import services as item_services
from babytroc.domains.item.models.image import ItemImage
from babytroc.domains.item.schemas.base import MonthRange
from babytroc.domains.item.schemas.create import ItemCreate
from babytroc.domains.user.services import get_user_by_email_private
from tests.fixtures.database.infrastructure.chain import SeedContext


async def _alice_image_at(db: AsyncSession, *, alice_id: int, offset: int) -> ItemImageRead:
    row = (
        await db.execute(
            select(ItemImage)
            .where(ItemImage.owner_id == alice_id)
            .order_by(ItemImage.name)
            .offset(offset)
            .limit(1)
        )
    ).scalar_one()
    return ItemImageRead.model_validate(row)


async def _alice_images_range(
    db: AsyncSession, *, alice_id: int, offset: int, limit: int,
) -> list[ItemImageRead]:
    rows = (
        await db.execute(
            select(ItemImage)
            .where(ItemImage.owner_id == alice_id)
            .order_by(ItemImage.name)
            .offset(offset)
            .limit(limit)
        )
    ).scalars().all()
    return [ItemImageRead.model_validate(r) for r in rows]


async def _bob_image_at(db: AsyncSession, *, bob_id: int) -> ItemImageRead:
    row = (
        await db.execute(
            select(ItemImage)
            .where(ItemImage.owner_id == bob_id)
            .order_by(ItemImage.name)
            .limit(1)
        )
    ).scalar_one()
    return ItemImageRead.model_validate(row)


async def seed_baseline_items(db: AsyncSession, ctx: SeedContext) -> None:
    """Insert alice_items, bob_items, alice_new_item, alice_special_item.

    Uses the 7 PBM images already seeded by `seed_baseline_images`. Image
    ordering is deterministic so SELECT-by-name returns identical results
    across runs.
    """
    del ctx
    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")

    alice_items_image = await _alice_image_at(db, alice_id=alice.id, offset=0)
    alice_new_item_images = await _alice_images_range(
        db, alice_id=alice.id, offset=1, limit=3,
    )
    alice_special_item_images = await _alice_images_range(
        db, alice_id=alice.id, offset=4, limit=2,
    )
    bob_items_image = await _bob_image_at(db, bob_id=bob.id)

    # alice_items[0]
    await item_services.create_item(
        db=db,
        owner_id=alice.id,
        item_create=ItemCreate(
            name="candle",
            description="dwell into a flowerbed",
            targeted_age_months=MonthRange("4-10"),
            regions={1},
            images=[alice_items_image.name],
        ),
    )

    # alice_new_item
    await item_services.create_item(
        db=db,
        owner_id=alice.id,
        item_create=ItemCreate(
            name="new-item",
            description="This is the latest new item created by alice.",
            targeted_age_months=MonthRange("7-"),
            regions={2},
            images=[img.name for img in alice_new_item_images],
        ),
    )

    # alice_special_item
    await item_services.create_item(
        db=db,
        owner_id=alice.id,
        item_create=ItemCreate(
            name="Special item",
            description="This is the special item created by alice.",
            targeted_age_months=MonthRange("2-5"),
            regions={1},
            images=[img.name for img in alice_special_item_images],
        ),
    )

    # bob_items[0]
    await item_services.create_item(
        db=db,
        owner_id=bob.id,
        item_create=ItemCreate(
            name="Dark side",
            description="Breathe, breathe in the air. Don't be afraid to care",
            targeted_age_months=MonthRange("16-"),
            regions={1, 2},
            images=[bob_items_image.name],
        ),
    )
```

- [ ] **Step 2: Verify import**

Run: `python -c "from tests.fixtures.database.seeds.item import seed_baseline_items"` (PYTHONPATH=src).

Expected: no output.

## Task 2.2: Register `tpl_baseline_items` and switch default

**Files:**
- Modify: `tests/fixtures/database/infrastructure/registry.py`

- [ ] **Step 1: Add `baseline_items` to `TEMPLATES`** in `tests/fixtures/database/infrastructure/registry.py`

```python
from tests.fixtures.database.seeds.item import seed_baseline_items
```

Add a new entry after `baseline`:

```python
    "baseline_items": TemplateSpec(
        name="baseline_items",
        parent="baseline",
        seeds=(seed_baseline_items,),
    ),
```

Change the default:

```python
DEFAULT_TEMPLATE = "baseline_items"
```

- [ ] **Step 2: Run a single non-item test to ensure default still works**

Run: `pytest tests/test_auth.py::TestAuthLogin::test_access_denied -v`

Expected: PASS.

## Task 2.3: Convert item/image fixtures in `tests/fixtures/items.py` to SELECT

The fixtures `alice_items`, `bob_items`, `alice_new_item`, `alice_special_item`, `alice_items_image`, `alice_new_item_images`, `alice_special_item_images`, `bob_items_image` currently *create* data. After this task they *read* data that the template already contains.

**Files:**
- Modify: `tests/fixtures/items.py`

- [ ] **Step 1: Replace the item-builder fixtures with SELECT versions**

In `tests/fixtures/items.py`, replace the current bodies of `alice_items`, `bob_items`, `alice_new_item`, `alice_special_item` (lines 217-287, 324-346) with SELECT-only versions. Image fixtures (lines 161-214) already do SELECT — leave as-is. The `alice_items_data`, `alice_new_item_data`, `alice_special_item_data`, `bob_items_data` fixtures stay (still useful for tests that want to compare expected vs DB content).

```python
# Replace alice_items (was: lines 217-239)
@pytest.fixture
async def alice_items(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[ItemRead]:
    """SELECT alice's baseline items by owner + name."""
    async with database_sessionmaker.begin() as session:
        rows = (
            await session.execute(
                select(item_services.models.item.Item)
                .where(item_services.models.item.Item.owner_id == alice.id)
                .where(item_services.models.item.Item.name == "candle")
            )
        ).scalars().all()
        return [ItemRead.model_validate(r) for r in rows]


# Replace alice_new_item (was: lines 242-263)
@pytest.fixture
async def alice_new_item(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> ItemRead:
    async with database_sessionmaker.begin() as session:
        row = (
            await session.execute(
                select(item_services.models.item.Item)
                .where(item_services.models.item.Item.owner_id == alice.id)
                .where(item_services.models.item.Item.name == "new-item")
            )
        ).scalar_one()
        return ItemRead.model_validate(row)


# Replace alice_special_item (was: lines 266-287)
@pytest.fixture
async def alice_special_item(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> ItemRead:
    async with database_sessionmaker.begin() as session:
        row = (
            await session.execute(
                select(item_services.models.item.Item)
                .where(item_services.models.item.Item.owner_id == alice.id)
                .where(item_services.models.item.Item.name == "Special item")
            )
        ).scalar_one()
        return ItemRead.model_validate(row)


# Replace bob_items (was: lines 324-346)
@pytest.fixture
async def bob_items(
    database_sessionmaker: async_sessionmaker,
    bob: UserPrivateRead,
) -> list[ItemRead]:
    async with database_sessionmaker.begin() as session:
        rows = (
            await session.execute(
                select(item_services.models.item.Item)
                .where(item_services.models.item.Item.owner_id == bob.id)
                .where(item_services.models.item.Item.name == "Dark side")
            )
        ).scalars().all()
        return [ItemRead.model_validate(r) for r in rows]
```

If `item_services.models.item.Item` is not the actual model location, locate `Item` via `grep -n "class Item" src/babytroc/domains/item/models/`. Update the import accordingly — likely `from babytroc.domains.item.models.item import Item` and use `Item` in the queries.

- [ ] **Step 2: Run item tests to verify they still pass**

Run: `pytest tests/item/ -v --no-header -p no:cacheprovider -x`

Expected: PASS for all tests in `tests/item/`. The class-scoped `database` override in `tests/item/conftest.py` is still in place — that gets removed in Phase 3.

- [ ] **Step 3: Run the full suite**

Run: `mise run test`

Expected: PASS.

- [ ] **Step 4: Commit Phase 2**

```bash
git add tests/fixtures/database/seeds/item.py \
        tests/fixtures/database/infrastructure/registry.py \
        tests/fixtures/items.py
git commit -m "$(cat <<'EOF'
test(db): add tpl_baseline_items, convert item fixtures to SELECT

alice_items / bob_items / alice_new_item / alice_special_item move from
function-scoped builders to function-scoped SELECT fixtures backed by the
new tpl_baseline_items template. Default template switches from
"baseline" to "baseline_items" so existing tests get the items
implicitly.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# PHASE 3 — Item-tier templates + `tests/item/` migration

End state: `tpl_many_items`, `tpl_alice_many_items`, `tpl_alice_items_with_categories`, `tpl_french_named_items` exist. `tests/item/` test classes carry markers; `tests/item/conftest.py` is gone; the class-scoped builder fixtures `many_items`, `alice_many_items`, `alice_items_with_categories`, `some_items_with_french_names` become function-scoped SELECT fixtures.

## Task 3.1: `seeds/item.py` — `seed_many_items`, `seed_alice_many_items`, `seed_french_named_items`

Move the bodies of today's `many_items` (tests/fixtures/items.py:362-413), `alice_many_items` (tests/fixtures/items.py:290-321), `some_items_with_french_names` (tests/fixtures/items.py:440-492) into seed functions. The fixed `random.seed(...)` values stay verbatim so seeded data matches today's data.

**Files:**
- Modify: `tests/fixtures/database/seeds/item.py`

- [ ] **Step 1: Append to `tests/fixtures/database/seeds/item.py`** (after `seed_baseline_items`)

```python
import random

from babytroc.domains.region.services import list_regions
from babytroc.infrastructure.cache_client import NullCache
from tests.utils import random_sample, random_str, random_targeted_age_months

_FRENCH_NAMES = [
    "Le sénat du bien-être",
    "Le senat bleus",
    "Les sénats bleus",
    "L'importance du Bien être",
    "La Lettre bleu",
    "Les lettres bleus",
    "Les mots bleus",
    "Le sénat bleu",
    "Les leçons données",
    "La lecon de mon ami",
    "La caravane bleue",
    "L'écriture bleue",
    "La cerise bleue",
]


async def seed_many_items(db: AsyncSession, ctx: SeedContext) -> None:
    """Create 256 mixed Alice/Bob items. Random seed: 0xBDF81829.

    Mirrors the old class-scoped `many_items` fixture exactly.
    """
    del ctx
    n = 256
    random.seed(0xBDF81829)

    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")
    alice_image = await _alice_image_at(db, alice_id=alice.id, offset=0)
    bob_image = await _bob_image_at(db, bob_id=bob.id)
    regions = await list_regions(db, NullCache())

    owner_ids, images = [
        list(column)
        for column in zip(
            *random.choices(
                [(alice.id, alice_image), (bob.id, bob_image)],
                k=n,
            ),
            strict=True,
        )
    ]

    await item_services.create_many_items(
        db=db,
        items=[
            item_services.create.CreateItem(
                owner_id=owner_id,
                item_create=ItemCreate(
                    name=random_str(8),
                    description=random_str(50),
                    targeted_age_months=random_targeted_age_months(),
                    regions=set(random_sample([reg.id for reg in regions])),
                    images=[image.name],
                    blocked=random.choice([False] * 3 + [True]),
                ),
            )
            for owner_id, image in zip(owner_ids, images, strict=True)
        ],
    )


async def seed_alice_many_items(db: AsyncSession, ctx: SeedContext) -> None:
    """Create 256 Alice-owned items, all `blocked=False`. Random seed: 0x25D4."""
    del ctx
    n = 256
    random.seed(0x25D4)

    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    alice_image = await _alice_image_at(db, alice_id=alice.id, offset=0)
    regions = await list_regions(db, NullCache())

    await item_services.create_many_items(
        db=db,
        items=[
            item_services.create.CreateItem(
                owner_id=alice.id,
                item_create=ItemCreate(
                    name=random_str(8),
                    description=random_str(50),
                    targeted_age_months=random_targeted_age_months(),
                    regions=set(random_sample([reg.id for reg in regions])),
                    images=[alice_image.name],
                    blocked=False,
                ),
            )
            for _ in range(n)
        ],
    )


async def seed_french_named_items(db: AsyncSession, ctx: SeedContext) -> None:
    """Create ~53 mixed Alice/Bob items with French-style names. Random seed: 0xA19F + 0x15976."""
    del ctx
    random.seed(0xA19F)
    names = [
        *_FRENCH_NAMES,
        *(f"{random_str(5)} bleu {random_str(5)}" for _ in range(40)),
    ]

    random.seed(0x15976)

    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")
    alice_image = await _alice_image_at(db, alice_id=alice.id, offset=0)
    bob_image = await _bob_image_at(db, bob_id=bob.id)
    regions = await list_regions(db, NullCache())

    owner_ids, images = [
        list(column)
        for column in zip(
            *random.choices(
                [(alice.id, alice_image), (bob.id, bob_image)],
                k=len(names),
            ),
            strict=True,
        )
    ]

    await item_services.create_many_items(
        db=db,
        items=[
            item_services.create.CreateItem(
                owner_id=owner_id,
                item_create=ItemCreate(
                    name=name,
                    description=random_str(50),
                    targeted_age_months=random_targeted_age_months(),
                    regions=set(random_sample([reg.id for reg in regions])),
                    images=[image.name],
                    blocked=random.choice([False] * 3 + [True]),
                ),
            )
            for name, owner_id, image in zip(names, owner_ids, images, strict=True)
        ],
    )
```

- [ ] **Step 2: Verify import**

Run: `python -c "from tests.fixtures.database.seeds.item import seed_many_items, seed_alice_many_items, seed_french_named_items"`.

Expected: no output.

## Task 3.2: `seeds/category.py::seed_alice_items_with_categories`

Move the body of `alice_items_with_categories` (tests/fixtures/categories.py:24-61) into a seed.

**Files:**
- Modify: `tests/fixtures/database/seeds/category.py`

- [ ] **Step 1: Append to `tests/fixtures/database/seeds/category.py`**

```python
import random

from sqlalchemy import insert, select

from babytroc.domains.category.services import list_categories
from babytroc.domains.item.models.category import ItemCategoryAssociation
from babytroc.domains.item.models.item import Item
from babytroc.domains.user.services import get_user_by_email_private
from babytroc.infrastructure.cache_client import NullCache


async def seed_alice_items_with_categories(db: AsyncSession, ctx: SeedContext) -> None:
    """Assign 1-3 random categories to each of Alice's many items. Seed: 0xCAFE."""
    del ctx
    random.seed(0xCAFE)

    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    categories = await list_categories(db, NullCache())
    child_categories = [c for c in categories if c.parent_slug is not None]

    item_ids = (
        await db.execute(select(Item.id).where(Item.owner_id == alice.id))
    ).scalars().all()

    associations = []
    for item_id in item_ids:
        chosen = random.sample(
            child_categories,
            k=random.randint(1, min(3, len(child_categories))),
        )
        for cat in chosen:
            associations.append({"item_id": item_id, "category_slug": cat.slug})

    if associations:
        await db.execute(insert(ItemCategoryAssociation).values(associations))
```

If the model import path is wrong, locate it via `grep -rn "class Item\b" src/babytroc/domains/item/models/`.

- [ ] **Step 2: Verify import**

Run: `python -c "from tests.fixtures.database.seeds.category import seed_alice_items_with_categories"`.

Expected: no output.

## Task 3.3: Register the four new templates

**Files:**
- Modify: `tests/fixtures/database/infrastructure/registry.py`

- [ ] **Step 1: Update imports and `TEMPLATES`**

Add imports:

```python
from tests.fixtures.database.seeds.category import seed_alice_items_with_categories
from tests.fixtures.database.seeds.item import (
    seed_alice_many_items,
    seed_french_named_items,
    seed_many_items,
)
```

Add entries after `baseline_items`:

```python
    "many_items": TemplateSpec(
        name="many_items",
        parent="baseline_items",
        seeds=(seed_many_items,),
    ),
    "alice_many_items": TemplateSpec(
        name="alice_many_items",
        parent="baseline_items",
        seeds=(seed_alice_many_items,),
    ),
    "alice_items_with_categories": TemplateSpec(
        name="alice_items_with_categories",
        parent="alice_many_items",
        seeds=(seed_alice_items_with_categories,),
    ),
    "french_named_items": TemplateSpec(
        name="french_named_items",
        parent="baseline_items",
        seeds=(seed_french_named_items,),
    ),
```

- [ ] **Step 2: Verify topological order**

Run: `python -c "from tests.fixtures.database.infrastructure.registry import TEMPLATES; from tests.fixtures.database.infrastructure.chain import _topo_sort; print(_topo_sort(TEMPLATES))"`.

Expected: `['bare', 'reference', 'baseline', 'baseline_items', 'many_items', 'alice_many_items', 'alice_items_with_categories', 'french_named_items']` (order between siblings of `baseline_items` may vary; that's OK).

## Task 3.4: Convert heavy item fixtures to SELECT

**Files:**
- Modify: `tests/fixtures/items.py` — `many_items`, `alice_many_items`, `some_items_with_french_names`
- Modify: `tests/fixtures/categories.py` — `alice_items_with_categories`

- [ ] **Step 1: Replace `many_items` in `tests/fixtures/items.py`** (was lines 362-413, scope="class")

```python
@pytest.fixture
async def many_items(
    database_sessionmaker: async_sessionmaker,
) -> list[ItemRead]:
    """SELECT all items from tpl_many_items (~256 + the 4 from baseline_items)."""
    from babytroc.domains.item.models.item import Item

    async with database_sessionmaker.begin() as session:
        rows = (
            await session.execute(select(Item).order_by(Item.id))
        ).scalars().all()
        return [ItemRead.model_validate(r) for r in rows]
```

- [ ] **Step 2: Replace `alice_many_items` in `tests/fixtures/items.py`** (was lines 290-321, scope="class")

```python
@pytest.fixture
async def alice_many_items(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[ItemRead]:
    """SELECT alice's items from tpl_alice_many_items (~256 + the baseline subset)."""
    from babytroc.domains.item.models.item import Item

    async with database_sessionmaker.begin() as session:
        rows = (
            await session.execute(
                select(Item).where(Item.owner_id == alice.id).order_by(Item.id)
            )
        ).scalars().all()
        return [ItemRead.model_validate(r) for r in rows]
```

- [ ] **Step 3: Replace `some_items_with_french_names` in `tests/fixtures/items.py`** (was lines 440-492, scope="class")

```python
@pytest.fixture
async def some_items_with_french_names(
    database_sessionmaker: async_sessionmaker,
    some_item_french_names: list[str],
) -> list[ItemRead]:
    """SELECT items whose name was seeded by tpl_french_named_items."""
    from babytroc.domains.item.models.item import Item

    async with database_sessionmaker.begin() as session:
        rows = (
            await session.execute(
                select(Item).where(Item.name.in_(some_item_french_names)).order_by(Item.id)
            )
        ).scalars().all()
        return [ItemRead.model_validate(r) for r in rows]
```

The `some_item_french_names` session-scoped fixture (lines 416-437) stays — it's the canonical name list that tests assert against.

- [ ] **Step 4: Replace `alice_items_with_categories` in `tests/fixtures/categories.py`** (was lines 24-61, scope="class")

```python
@pytest.fixture
async def alice_items_with_categories(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[ItemRead]:
    """SELECT alice's items + categories from tpl_alice_items_with_categories."""
    from babytroc.domains.item.services import get_many_items
    from babytroc.domains.item.models.item import Item

    async with database_sessionmaker() as session:
        ids = (
            await session.execute(select(Item.id).where(Item.owner_id == alice.id))
        ).scalars().all()
        return await get_many_items(db=session, item_ids=set(ids))
```

## Task 3.5: Add markers to `tests/item/` test classes

Map each class to its template:

| File | Class | Template |
| --- | --- | --- |
| `tests/item/test_item_read.py` | `TestItemReadMany` etc. (uses `many_items`) | `many_items` |
| `tests/item/test_item_read.py` | classes using `some_items_with_french_names` | `french_named_items` |
| `tests/item/test_item_like.py` | classes using `many_items` | `many_items` |
| `tests/item/test_item_categories.py` | classes using `alice_items_with_categories` | `alice_items_with_categories` |

Other `tests/item/test_*.py` classes don't use heavy fixtures — leave unmarked (they get default `baseline_items`).

**Files:**
- Modify: `tests/item/test_item_read.py`
- Modify: `tests/item/test_item_like.py`
- Modify: `tests/item/test_item_categories.py`

- [ ] **Step 1: For each class that uses `many_items`, add a marker above the class declaration**

In `tests/item/test_item_read.py`, find the lines `@pytest.mark.usefixtures("many_items")` (lines 14, 50, 147, 224, 285) — *keep* those (they declare the fixture dependency); add a `db_template` marker on the same class:

```python
@pytest.mark.db_template("many_items")
@pytest.mark.usefixtures("many_items")
class TestItemReadMany:
    ...
```

For classes using `some_items_with_french_names` (line 331 in `tests/item/test_item_read.py`):

```python
@pytest.mark.db_template("french_named_items")
@pytest.mark.usefixtures("some_items_with_french_names")
class TestItemReadFrench:
    ...
```

- [ ] **Step 2: In `tests/item/test_item_like.py`** add `@pytest.mark.db_template("many_items")` to the class on line 7.

- [ ] **Step 3: In `tests/item/test_item_categories.py`** add `@pytest.mark.db_template("alice_items_with_categories")` to each class that uses `alice_items_with_categories`.

## Task 3.6: Delete `tests/item/conftest.py`

**Files:**
- Delete: `tests/item/conftest.py`

- [ ] **Step 1: Remove the file**

```bash
git rm tests/item/conftest.py
```

- [ ] **Step 2: Run the item tests**

Run: `pytest tests/item/ -v --no-header -p no:cacheprovider -x`

Expected: PASS — every class either has a marker selecting a richer template or uses the default `baseline_items`.

If a test fails because a class assumed class-scoped `database` (state preserved across methods), audit that class — the spec is explicit that per-method clones replace class-scoped DBs. Convert any inter-method state into seed data via a new chain template, OR rewrite the class so each method is self-contained.

- [ ] **Step 3: Run the full suite**

Run: `mise run test`

Expected: PASS.

- [ ] **Step 4: Commit Phase 3**

```bash
git add tests/fixtures/database tests/fixtures/items.py tests/fixtures/categories.py tests/item/
git rm tests/item/conftest.py
git commit -m "$(cat <<'EOF'
test(db): item-tier templates, drop tests/item/conftest.py

Adds tpl_many_items, tpl_alice_many_items, tpl_alice_items_with_categories,
tpl_french_named_items. Heavy class-scoped item fixtures become
function-scoped SELECT fixtures backed by these templates. tests/item/
classes carry @pytest.mark.db_template; the class-scoped database
override is gone — per-method clones now replace it.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# PHASE 4 — Loan-tier templates + `tests/loan/` migration

End state: `tpl_many_users`, `tpl_alice_special_item_loan_requests`, `tpl_many_loan_requests` (built on `many_items`), `tpl_alice_many_loans` (built on `alice_many_items`) exist. `tests/loan/` test classes carry markers; `tests/loan/conftest.py` is gone; `many_users`, `many_loan_requests_for_alice_items`, `many_loan_requests_for_alice_special_item`, `alice_many_loans` become SELECT fixtures.

## Task 4.1: `seeds/user.py::seed_many_users`

**Files:**
- Modify: `tests/fixtures/database/seeds/user.py`

- [ ] **Step 1: Append `seed_many_users` to `tests/fixtures/database/seeds/user.py`**

```python
import random
from string import ascii_letters

from babytroc.shared.hash import HashedStr
from babytroc.domains.user.schemas.create import UserCreate


def _random_str(length: int) -> str:
    return "".join(random.choices(ascii_letters, k=length))


async def seed_many_users(db: AsyncSession, ctx: SeedContext) -> None:
    """Create 256 random users. Random seed: 0x538D."""
    del ctx
    n = 256
    random.seed(0x538D)

    password_hash = HashedStr("xyzXYZ123")

    user_creates = [
        UserCreate(
            name=_random_str(8),
            email=f"{_random_str(8)}@{_random_str(8)}.com",
            password=password_hash,
        )
        for _ in range(n)
    ]

    await create_many_users_without_validation(
        db=db,
        user_creates=user_creates,
        validated=True,
    )
```

- [ ] **Step 2: Verify import**

Run: `python -c "from tests.fixtures.database.seeds.user import seed_many_users"`.

Expected: no output.

## Task 4.2: `seeds/loan.py` — three loan seeds

**Files:**
- Create: `tests/fixtures/database/seeds/loan.py`

- [ ] **Step 1: Create `tests/fixtures/database/seeds/loan.py`** with all three loan seeds

```python
"""Loan seeds — bulk loan requests and loans on top of item-bearing templates."""

import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.item.models.item import Item
from babytroc.domains.loan import services as loan_services
from babytroc.domains.loan.enums import LoanRequestState
from babytroc.domains.loan.schemas.base import ItemBorrowerId
from babytroc.domains.user.models import User
from babytroc.domains.user.services import get_user_by_email_private
from tests.fixtures.database.infrastructure.chain import SeedContext
from tests.utils import split


async def _alice_special_item(db: AsyncSession, *, alice_id: int) -> Item:
    return (
        await db.execute(
            select(Item).where(Item.owner_id == alice_id).where(Item.name == "Special item")
        )
    ).scalar_one()


async def seed_many_loan_requests_for_alice_items(db: AsyncSession, ctx: SeedContext) -> None:
    """Cancelled/rejected/accepted/executed/pending requests on alice's `many_items`. Seed: 0x32D1.

    Mirrors the old `many_loan_requests_for_alice_items` class fixture exactly.
    """
    del ctx
    random.seed(0x32D1)

    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")
    carol = await get_user_by_email_private(db=db, email="carol@babytroc.ch")

    alice_items = (
        await db.execute(select(Item).where(Item.owner_id == alice.id))
    ).scalars().all()

    items_to_request = random.sample(alice_items, k=round(0.9 * len(alice_items)))
    borrowers = [bob, carol]

    new_loan_requests = await loan_services.create_many_loan_requests(
        db=db,
        loan_requests={
            ItemBorrowerId.from_values(item_id=item.id, borrower_id=borrower.id)
            for item, borrower in zip(
                items_to_request,
                random.choices(borrowers, k=len(items_to_request)),
                strict=True,
            )
        },
    )

    selected, _remaining = split(
        random.sample(new_loan_requests, k=len(new_loan_requests)), 2,
    )
    to_execute, selected = selected[:1], selected[1:]
    to_cancel, to_reject, to_accept = split(selected, 3)

    await loan_services.cancel_many_loan_requests(
        db=db, loan_request_ids={r.id for r in to_cancel}, send_messages=False,
    )
    await loan_services.reject_many_loan_requests(
        db=db, loan_request_ids={r.id for r in to_reject}, send_messages=False,
    )
    await loan_services.accept_many_loan_requests(
        db=db, loan_request_ids={r.id for r in to_accept}, send_messages=False,
    )
    await loan_services.execute_many_loan_requests(
        db=db,
        loan_request_ids={r.id for r in to_execute},
        send_messages=False,
        check_state=False,
    )

    # Verify minimum counts per state (matches old fixture's runtime check)
    final = (
        await db.execute(select(loan_services.models.loan_request.LoanRequest))
    ).scalars().all()
    for state in LoanRequestState:
        if state == LoanRequestState.executed:
            continue
        if sum(1 for r in final if r.state == state) < 10:
            msg = f"There must be at least 10 {state.name} loan requests"
            raise ValueError(msg)


async def seed_alice_special_item_loan_requests(db: AsyncSession, ctx: SeedContext) -> None:
    """Many users requesting alice's special item, varied states. Seed: 0x50E6."""
    del ctx
    random.seed(0x50E6)

    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    special = await _alice_special_item(db, alice_id=alice.id)

    # the 256 users seeded by seed_many_users — exclude the 3 baseline names
    extra_users = (
        await db.execute(
            select(User).where(User.email.notin_([
                "alice@babytroc.ch", "bob@babytroc.ch", "carol@babytroc.ch",
            ]))
        )
    ).scalars().all()

    borrowers = random.sample(extra_users, k=round(0.9 * len(extra_users)))

    new_loan_requests = await loan_services.create_many_loan_requests(
        db=db,
        item_ids=special.id,
        borrower_ids={u.id for u in borrowers},
    )

    selected, _remaining = split(
        random.sample(new_loan_requests, k=len(new_loan_requests)), 2,
    )
    to_execute, selected = selected[:1], selected[1:]
    to_cancel, to_reject, to_accept = split(selected, 3)

    await loan_services.cancel_many_loan_requests(
        db=db, loan_request_ids={r.id for r in to_cancel}, send_messages=False,
    )
    await loan_services.reject_many_loan_requests(
        db=db, loan_request_ids={r.id for r in to_reject}, send_messages=False,
    )
    await loan_services.accept_many_loan_requests(
        db=db, loan_request_ids={r.id for r in to_accept}, send_messages=False,
    )
    await loan_services.execute_many_loan_requests(
        db=db,
        loan_request_ids={r.id for r in to_execute},
        send_messages=False,
        check_state=False,
    )


async def seed_alice_many_loans(db: AsyncSession, ctx: SeedContext) -> None:
    """Loans on alice's `alice_many_items`, half ended, half restarted. Seed: 0x50E6.

    Mirrors the old `alice_many_loans` class fixture exactly.
    """
    del ctx
    random.seed(0x50E6)

    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")
    carol = await get_user_by_email_private(db=db, email="carol@babytroc.ch")
    borrowers = [bob, carol]

    alice_items = (
        await db.execute(select(Item).where(Item.owner_id == alice.id))
    ).scalars().all()
    items = random.sample(alice_items, k=round(0.5 * len(alice_items)))

    loan_requests = await loan_services.create_many_loan_requests(
        db=db,
        loan_requests={
            ItemBorrowerId.from_values(item_id=item.id, borrower_id=borrower.id)
            for item, borrower in zip(
                items,
                random.choices(borrowers, k=len(items)),
                strict=True,
            )
        },
    )

    loans = await loan_services.execute_many_loan_requests(
        db=db,
        loan_request_ids={r.id for r in loan_requests},
        check_state=False,
    )

    ended_loans = await loan_services.end_many_loans(
        db=db, loan_ids={l.id for l in random.sample(loans, k=round(len(loans) * 0.7))},
    )

    items_to_request_again = [
        loan.item for loan in random.sample(ended_loans, k=len(ended_loans) // 2)
    ]
    loan_requests = await loan_services.create_many_loan_requests(
        db=db,
        loan_requests={
            ItemBorrowerId.from_values(item_id=item.id, borrower_id=borrower.id)
            for item, borrower in zip(
                items_to_request_again,
                random.choices(borrowers, k=len(items_to_request_again)),
                strict=True,
            )
        },
    )
    restarted_loans = await loan_services.execute_many_loan_requests(
        db=db,
        loan_request_ids={r.id for r in loan_requests},
        check_state=False,
    )
    _restarted, ended_twice = split(restarted_loans, 2)
    await loan_services.end_many_loans(
        db=db, loan_ids={l.id for l in ended_twice},
    )
```

If any model path is wrong (e.g. `User`, `LoanRequest`), locate the canonical paths via `grep -rn "class User\b" src/babytroc/domains/user/models*.py` and `grep -rn "class LoanRequest" src/babytroc/domains/loan/models/`.

- [ ] **Step 2: Verify import**

Run: `python -c "from tests.fixtures.database.seeds.loan import seed_many_loan_requests_for_alice_items, seed_alice_special_item_loan_requests, seed_alice_many_loans"`.

Expected: no output.

## Task 4.3: Register the four new templates

**Files:**
- Modify: `tests/fixtures/database/infrastructure/registry.py`

- [ ] **Step 1: Update imports and `TEMPLATES`**

Add imports:

```python
from tests.fixtures.database.seeds.loan import (
    seed_alice_many_loans,
    seed_alice_special_item_loan_requests,
    seed_many_loan_requests_for_alice_items,
)
from tests.fixtures.database.seeds.user import seed_many_users
```

Add entries:

```python
    "many_users": TemplateSpec(
        name="many_users",
        parent="baseline_items",
        seeds=(seed_many_users,),
    ),
    "alice_special_item_loan_requests": TemplateSpec(
        name="alice_special_item_loan_requests",
        parent="many_users",
        seeds=(seed_alice_special_item_loan_requests,),
    ),
    "many_loan_requests": TemplateSpec(
        name="many_loan_requests",
        parent="many_items",
        seeds=(seed_many_loan_requests_for_alice_items,),
    ),
    "alice_many_loans": TemplateSpec(
        name="alice_many_loans",
        parent="alice_many_items",
        seeds=(seed_alice_many_loans,),
    ),
```

- [ ] **Step 2: Verify topological order**

Run: `python -c "from tests.fixtures.database.infrastructure.registry import TEMPLATES; from tests.fixtures.database.infrastructure.chain import _topo_sort; print(_topo_sort(TEMPLATES))"`.

Expected: 12 entries (Phase 1: 3, Phase 2: 1, Phase 3: 4, Phase 4: 4).

## Task 4.4: Convert heavy loan + user fixtures to SELECT

**Files:**
- Modify: `tests/fixtures/users.py` — `many_users`
- Modify: `tests/fixtures/loans.py` — `many_loan_requests_for_alice_items`, `many_loan_requests_for_alice_special_item`, `alice_many_loans`

- [ ] **Step 1: Replace `many_users` in `tests/fixtures/users.py`** (was lines 87-112, scope="class")

```python
@pytest.fixture
async def many_users(
    database_sessionmaker: async_sessionmaker,
) -> list[UserPrivateRead]:
    """SELECT all users from tpl_many_users (~256 + the 3 baseline)."""
    from sqlalchemy import select
    from babytroc.domains.user.models import User

    async with database_sessionmaker.begin() as session:
        rows = (
            await session.execute(select(User).order_by(User.id))
        ).scalars().all()
        return [UserPrivateRead.model_validate(r) for r in rows]
```

- [ ] **Step 2: Replace `many_loan_requests_for_alice_items` in `tests/fixtures/loans.py`** (was lines 136-272, scope="class")

```python
@pytest.fixture
async def many_loan_requests_for_alice_items(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[LoanRequestRead]:
    from sqlalchemy import select
    from babytroc.domains.item.models.item import Item
    from babytroc.domains.loan.models.loan_request import LoanRequest

    async with database_sessionmaker.begin() as session:
        rows = (
            await session.execute(
                select(LoanRequest)
                .join(Item, Item.id == LoanRequest.item_id)
                .where(Item.owner_id == alice.id)
                .order_by(LoanRequest.id)
            )
        ).scalars().all()
        return [LoanRequestRead.model_validate(r) for r in rows]
```

- [ ] **Step 3: Replace `many_loan_requests_for_alice_special_item` in `tests/fixtures/loans.py`** (was lines 275-394, scope="class")

```python
@pytest.fixture
async def many_loan_requests_for_alice_special_item(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    alice_special_item: ItemRead,
) -> list[LoanRequestRead]:
    from sqlalchemy import select
    from babytroc.domains.loan.models.loan_request import LoanRequest

    async with database_sessionmaker.begin() as session:
        rows = (
            await session.execute(
                select(LoanRequest)
                .where(LoanRequest.item_id == alice_special_item.id)
                .order_by(LoanRequest.id)
            )
        ).scalars().all()
        return [LoanRequestRead.model_validate(r) for r in rows]
```

- [ ] **Step 4: Replace `alice_many_loans` in `tests/fixtures/loans.py`** (was lines 397-502, scope="class")

```python
@pytest.fixture
async def alice_many_loans(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[LoanRead]:
    from sqlalchemy import select
    from babytroc.domains.item.models.item import Item
    from babytroc.domains.loan.models.loan import Loan

    async with database_sessionmaker.begin() as session:
        rows = (
            await session.execute(
                select(Loan)
                .join(Item, Item.id == Loan.item_id)
                .where(Item.owner_id == alice.id)
                .order_by(Loan.id)
            )
        ).scalars().all()
        return [LoanRead.model_validate(r) for r in rows]
```

If any model path is wrong, locate via `grep -rn "class LoanRequest\b\|class Loan\b" src/babytroc/domains/loan/models/`.

## Task 4.5: Add markers to `tests/loan/` test classes

| File | Class | Template |
| --- | --- | --- |
| `tests/loan/test_loan_requests_read.py` | classes using `many_loan_requests_for_alice_items` (line 14) | `many_loan_requests` |
| `tests/loan/test_loan_requests_read.py` | classes using `many_loan_requests_for_alice_special_item` | `alice_special_item_loan_requests` |
| `tests/loan/test_loans_read.py` | classes using `alice_many_loans` | `alice_many_loans` |

Other `tests/loan/test_*.py` classes use only function-scoped fixtures — leave unmarked.

**Files:**
- Modify: `tests/loan/test_loan_requests_read.py`
- Modify: `tests/loan/test_loans_read.py`

- [ ] **Step 1: Add `@pytest.mark.db_template("many_loan_requests")` above the class on line 14 of `tests/loan/test_loan_requests_read.py`**

```python
@pytest.mark.db_template("many_loan_requests")
@pytest.mark.usefixtures("many_loan_requests_for_alice_items")
class TestLoanRequestsReadMany:
    ...
```

- [ ] **Step 2: Add `@pytest.mark.db_template("alice_special_item_loan_requests")` above the class that consumes `many_loan_requests_for_alice_special_item`** (around line 110-128)

- [ ] **Step 3: Add `@pytest.mark.db_template("alice_many_loans")` above each class in `tests/loan/test_loans_read.py` that uses `alice_many_loans`**

## Task 4.6: Delete `tests/loan/conftest.py`

**Files:**
- Delete: `tests/loan/conftest.py`

- [ ] **Step 1: Remove the file**

```bash
git rm tests/loan/conftest.py
```

- [ ] **Step 2: Run loan tests**

Run: `pytest tests/loan/ -v --no-header -p no:cacheprovider -x`

Expected: PASS.

- [ ] **Step 3: Run the full suite**

Run: `mise run test`

Expected: PASS.

- [ ] **Step 4: Commit Phase 4**

```bash
git add tests/fixtures/database tests/fixtures/users.py tests/fixtures/loans.py tests/loan/
git rm tests/loan/conftest.py
git commit -m "$(cat <<'EOF'
test(db): loan-tier templates, drop tests/loan/conftest.py

Adds tpl_many_users, tpl_alice_special_item_loan_requests,
tpl_many_loan_requests, tpl_alice_many_loans. Heavy class-scoped fixtures
many_users / many_loan_requests_for_alice_items /
many_loan_requests_for_alice_special_item / alice_many_loans become
function-scoped SELECT fixtures. tests/loan/ classes carry markers; the
class-scoped database override is gone.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# PHASE 5 — Chat-tier template + `tests/chat_read/` migration

End state: `tpl_alice_many_chats` exists. `tests/chat_read/test_chat_read.py` carries a marker; `tests/chat_read/conftest.py` is gone; `alice_many_chats` becomes a SELECT fixture.

## Task 5.1: `seeds/chat.py::seed_alice_many_chats`

Move the body of `alice_many_chats` (tests/fixtures/chat.py:194-219) into a seed. The fixture already runs against `many_items`, so the seed parent is `many_items`.

**Files:**
- Create: `tests/fixtures/database/seeds/chat.py`

- [ ] **Step 1: Create `tests/fixtures/database/seeds/chat.py`**

```python
"""Chat seeds — alice_many_chats on top of many_items."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.item.models.item import Item
from babytroc.domains.loan import services as loan_services
from babytroc.domains.user.services import get_user_by_email_private
from tests.fixtures.database.infrastructure.chain import SeedContext


async def seed_alice_many_chats(db: AsyncSession, ctx: SeedContext) -> None:
    """Create one loan request per alice/bob item, generating the chat for each."""
    del ctx
    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")

    items = (
        await db.execute(
            select(Item).where(Item.owner_id.in_({alice.id, bob.id}))
        )
    ).scalars().all()

    for item in items:
        borrower_id = alice.id if item.owner_id == bob.id else bob.id
        await loan_services.create_loan_request(
            db=db, item_id=item.id, borrower_id=borrower_id,
        )
```

- [ ] **Step 2: Verify import**

Run: `python -c "from tests.fixtures.database.seeds.chat import seed_alice_many_chats"`.

Expected: no output.

## Task 5.2: Register `tpl_alice_many_chats`

**Files:**
- Modify: `tests/fixtures/database/infrastructure/registry.py`

- [ ] **Step 1: Add to `TEMPLATES`**

Add import:

```python
from tests.fixtures.database.seeds.chat import seed_alice_many_chats
```

Add entry:

```python
    "alice_many_chats": TemplateSpec(
        name="alice_many_chats",
        parent="many_items",
        seeds=(seed_alice_many_chats,),
    ),
```

- [ ] **Step 2: Verify topological order**

Run: `python -c "from tests.fixtures.database.infrastructure.registry import TEMPLATES; from tests.fixtures.database.infrastructure.chain import _topo_sort; print(len(_topo_sort(TEMPLATES)))"`.

Expected: `13`.

## Task 5.3: Convert `alice_many_chats` to SELECT

**Files:**
- Modify: `tests/fixtures/chat.py`

- [ ] **Step 1: Replace `alice_many_chats` (was lines 194-219, scope="class")**

```python
@pytest.fixture
async def alice_many_chats(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    bob: UserPrivateRead,
) -> list[ChatRead]:
    """SELECT every chat between Alice and Bob."""
    from sqlalchemy import or_, select
    from babytroc.domains.chat.models import Chat

    async with database_sessionmaker.begin() as session:
        rows = (
            await session.execute(
                select(Chat).where(
                    or_(
                        (Chat.member_a_id == alice.id) & (Chat.member_b_id == bob.id),
                        (Chat.member_a_id == bob.id) & (Chat.member_b_id == alice.id),
                    )
                ).order_by(Chat.id)
            )
        ).scalars().all()
        return [ChatRead.model_validate(r) for r in rows]
```

If the `Chat` model path is wrong, locate via `grep -rn "class Chat\b" src/babytroc/domains/chat/models*.py`. The actual member field names may differ (`member_a_id`/`member_b_id` vs `user1_id`/`user2_id` vs a join table) — `grep -n "id\|user\|member" src/babytroc/domains/chat/models.py` will reveal the schema. Adjust the WHERE clause accordingly.

## Task 5.4: Add marker to `tests/chat_read/test_chat_read.py`

**Files:**
- Modify: `tests/chat_read/test_chat_read.py`

- [ ] **Step 1: Add `@pytest.mark.db_template("alice_many_chats")` above the class on line ~17-19 (the one consuming `alice_many_chats`)**

```python
@pytest.mark.db_template("alice_many_chats")
class TestChatRead:
    async def test_x(self, alice_many_chats: list[ChatRead], ...):
        ...
```

## Task 5.5: Delete `tests/chat_read/conftest.py`

**Files:**
- Delete: `tests/chat_read/conftest.py`

- [ ] **Step 1: Remove the file**

```bash
git rm tests/chat_read/conftest.py
```

- [ ] **Step 2: Run chat_read tests**

Run: `pytest tests/chat_read/ -v --no-header -p no:cacheprovider -x`

Expected: PASS.

- [ ] **Step 3: Run the full suite**

Run: `mise run test`

Expected: PASS — full migration complete.

- [ ] **Step 4: Commit Phase 5**

```bash
git add tests/fixtures/database tests/fixtures/chat.py tests/chat_read/
git rm tests/chat_read/conftest.py
git commit -m "$(cat <<'EOF'
test(db): chat-tier template, drop tests/chat_read/conftest.py

Adds tpl_alice_many_chats. alice_many_chats becomes a function-scoped
SELECT fixture; tests/chat_read/test_chat_read.py carries the marker.
This completes the migration: 13 templates total, no class-scoped
database overrides remain, every test gets a fresh per-method clone.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# Final verification

- [ ] **Run full suite once more under parallelism**

Run: `mise run test`

Expected: PASS, similar or better wall-clock time vs before.

- [ ] **Confirm no class-scoped DB overrides remain**

Run: `grep -rn '@pytest.fixture(scope="class")\s*$' tests/ --include="*.py" | grep -E "(database|primary_database|database_sessionmaker)"`

Expected: empty output (no matches).

- [ ] **Confirm marker coverage**

Run: `grep -rn "db_template" tests/ --include="*.py" | grep -v "fixtures/database/" | wc -l`

Expected: at least 6 occurrences (one per heavy class — item_read many, item_read french, item_like, item_categories, loan_requests_read many, loan_requests_read special, loans_read alice_many, chat_read).

- [ ] **Smoke test heavy paths in isolation**

Run: `pytest tests/loan/test_loans_read.py tests/loan/test_loan_requests_read.py tests/item/test_item_read.py tests/chat_read/ -v -x`

Expected: PASS.

---

# Risks revisited

- **Model import paths in seeds/SELECTs.** Several SELECT fixtures and seeds reference `from babytroc.domains.X.models...` paths inferred from the project layout. If imports fail, locate the canonical path via grep at the import site — these are not load-bearing decisions, just transcription details.
- **`item_services.models.item.Item` access.** Phase 2 fixtures reference `item_services.models.item.Item` for queries; if `item_services` doesn't re-export the model, switch to a direct import as already shown in Phase 3 (`from babytroc.domains.item.models.item import Item`).
- **Random-seed determinism.** Each seed call sets `random.seed(...)` to the same value the old fixture used. This is critical: `tests/loan/test_loan_requests_read.py` asserts on counts per state (≥10 cancelled, ≥10 rejected, etc.). If those asserts fail post-migration, the random sequences are not actually identical — most likely cause is the order in which `random` is consumed inside the seed differing from inside the original fixture. Inspect the original fixture body and match the consumption order line-for-line.
- **Stale connections blocking `CREATE DATABASE TEMPLATE`.** The chain builder uses `run_against` which disposes the engine in a finally block. If a future seed forgets to use it and leaks a connection, the next chain step will fail with "source database is being accessed by other users". Guard rule: every seed receives an `AsyncSession`, and the chain owns the engine lifecycle.
