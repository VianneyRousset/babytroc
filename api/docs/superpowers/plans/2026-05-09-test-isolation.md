# Test Isolation Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Per-function database isolation for tests — every test gets a fresh DB clone, eliminating flaky parallel failures.

**Architecture:** Session-scoped template DB with seeded reference data (users, regions, categories, images). Function-scoped DB clone per test. Worker-scoped FastAPI app with DB swap per test. Heavy pagination tests keep class-scoped DB via local conftest overrides.

**Tech Stack:** pytest, pytest-xdist, PostgreSQL CREATE DATABASE TEMPLATE, SQLAlchemy async

**Spec:** `docs/superpowers/specs/2026-05-09-test-isolation-design.md`

---

## File Structure

```
Modified:
  tests/fixtures/database.py    — template seeding, function-scoped database
  tests/fixtures/app.py         — session-scoped app, autouse DB swap + Redis flush
  tests/fixtures/users.py       — function-scoped SELECT (no INSERT)
  tests/fixtures/regions.py     — function-scoped SELECT
  tests/fixtures/categories.py  — function-scoped SELECT
  tests/fixtures/items.py       — image fixtures → function-scoped SELECT, data fixtures → session constants
  tests/fixtures/loans.py       — heavy fixtures stay class-scoped (used via conftest override)
  tests/fixtures/chat.py        — class-scoped fixtures → function-scoped
  tests/fixtures/websockets.py  — no change (already function-scoped)
  tests/fixtures/clients.py     — no change (already function-scoped)
  tests/fixtures/s3.py          — no change (already session-scoped)
  tests/conftest.py             — no change
  pyproject.toml                — no change needed

Created:
  tests/item/conftest.py                — class-scoped database override for heavy item tests
  tests/loan/conftest.py                — class-scoped database override for heavy loan tests
  tests/chat/conftest.py                — class-scoped database override for heavy chat tests (test_chat_read.py)
```

---

## Important Design Decision: Dual Scope Strategy

6 test files use heavy fixtures creating 256+ items/loans/users. Making those function-scoped would add ~4s per test (~120s total). Instead:

- **Default**: function-scoped `database` fixture (most tests)
- **Heavy test dirs**: local `conftest.py` overrides `database` back to class-scoped

Heavy test files: `test_item_read.py`, `test_item_like.py`, `test_item_categories.py`, `test_loans_read.py`, `test_loan_requests_read.py`, `test_chat_read.py`.

These tests are read-only within each test function — class-scoped DB is safe for them because they don't mutate shared state between tests.

---

## Task 1: Seed reference data in primary_database

**Files:**
- Modify: `tests/fixtures/database.py`

The `primary_database` fixture currently only runs alembic migrations. Add seeding of users, regions, categories, and images into the template.

- [ ] **Step 1: Rewrite `tests/fixtures/database.py`**

```python
# tests/fixtures/database.py
import asyncio
import os
import warnings
from collections.abc import AsyncGenerator
from functools import partial
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.config import Config as AlembicConfig
from sqlalchemy import URL, text
from sqlalchemy.exc import SAWarning
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from alembic import command

# make sqlalchemy warnings as errors
warnings.simplefilter("error", SAWarning)


def run_alembic_upgrade_head(url: URL):
    app_root = Path(__file__).parent.parent.parent
    alembic_cfg = AlembicConfig(app_root / "alembic.ini")
    alembic_cfg.set_main_option(
        "script_location", str(app_root / "alembic"),
    )
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        url.render_as_string(hide_password=False),
    )
    command.upgrade(alembic_cfg, "head")


async def _seed_template(url: URL) -> None:
    """Seed users, regions, categories, images into template DB."""

    from babytroc.domains.category.schemas.create import CategoryCreate
    from babytroc.domains.category import services as category_services
    from babytroc.domains.image import services as image_services
    from babytroc.domains.region.schemas.create import RegionCreate
    from babytroc.domains.region import services as region_services
    from babytroc.domains.user.schemas.create import UserCreate
    from babytroc.domains.user import services as user_services
    from babytroc.infrastructure.config import Config, S3Config

    engine = create_async_engine(url, poolclass=NullPool)
    maker = async_sessionmaker(bind=engine)

    config = Config.from_env(
        s3=S3Config(
            endpoint_url="http://localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket="test-bucket",
            public_url="http://localhost:9000/test-bucket",
        ),
    )

    # --- users ---
    async with maker.begin() as session:
        await user_services.create_many_users_without_validation(
            session,
            [
                UserCreate(
                    name="alice",
                    email="alice@babytroc.ch",
                    password="password-Alice-42",
                ),
                UserCreate(
                    name="bob",
                    email="bob@babytroc.ch",
                    password="password-Bob-42",
                ),
                UserCreate(
                    name="carol",
                    email="carol@babytroc.ch",
                    password="password-Carol-42",
                ),
            ],
            validated=True,
        )

    # --- regions ---
    async with maker.begin() as session:
        await region_services.create_region(
            session, RegionCreate(id=1, name="region1"),
        )
        await region_services.create_region(
            session, RegionCreate(id=2, name="region2"),
        )

    # --- categories ---
    parents = [
        CategoryCreate(slug="clothing", name="Vêtements"),
        CategoryCreate(slug="toys", name="Jouets"),
        CategoryCreate(slug="gear", name="Équipement"),
    ]
    children = [
        CategoryCreate(
            slug="clothing-bodysuits",
            name="Bodies",
            parent_slug="clothing",
        ),
        CategoryCreate(
            slug="clothing-sleepwear",
            name="Pyjamas",
            parent_slug="clothing",
        ),
        CategoryCreate(
            slug="clothing-outerwear",
            name="Manteaux",
            parent_slug="clothing",
        ),
        CategoryCreate(
            slug="clothing-accessories",
            name="Accessoires",
            parent_slug="clothing",
        ),
        CategoryCreate(
            slug="toys-bath",
            name="Jouets de bain",
            parent_slug="toys",
        ),
        CategoryCreate(
            slug="toys-soft",
            name="Peluches",
            parent_slug="toys",
        ),
        CategoryCreate(
            slug="toys-educational",
            name="Jouets éducatifs",
            parent_slug="toys",
        ),
        CategoryCreate(
            slug="gear-strollers",
            name="Poussettes",
            parent_slug="gear",
        ),
        CategoryCreate(
            slug="gear-car-seats",
            name="Sièges auto",
            parent_slug="gear",
        ),
        CategoryCreate(
            slug="gear-carriers",
            name="Porte-bébés",
            parent_slug="gear",
        ),
    ]

    async with maker.begin() as session:
        await category_services.create_many_categories(
            session, category_creates=parents,
        )
        await category_services.create_many_categories(
            session, category_creates=children,
        )

    # --- images ---
    # PBM image data (different patterns for different image sets)
    alice_items_img = (
        "P1\n3 3\n101\n101\n010"
    ).encode()
    alice_new_item_img = (
        "P1\n3 3\n000\n111\n000"
    ).encode()
    alice_special_item_img = (
        "P1\n3 3\n101\n111\n010"
    ).encode()
    bob_items_img = (
        "P1\n3 3\n101\n101\n010"
    ).encode()

    # Look up user IDs
    async with maker.begin() as session:
        alice = await user_services.get_user_by_email_private(
            session, "alice@babytroc.ch",
        )
        bob = await user_services.get_user_by_email_private(
            session, "bob@babytroc.ch",
        )

    # Upload images: alice_items (1), alice_new_item (3),
    # alice_special_item (2), bob_items (1)
    async with maker.begin() as session:
        await image_services.upload_image(
            db=session, config=config,
            owner_id=alice.id, fp=BytesIO(alice_items_img),
        )
        for _ in range(3):
            await image_services.upload_image(
                db=session, config=config,
                owner_id=alice.id, fp=BytesIO(alice_new_item_img),
            )
        for _ in range(2):
            await image_services.upload_image(
                db=session, config=config,
                owner_id=alice.id, fp=BytesIO(alice_special_item_img),
            )
        await image_services.upload_image(
            db=session, config=config,
            owner_id=bob.id, fp=BytesIO(bob_items_img),
        )

    await engine.dispose()


@pytest.fixture(scope="session")
async def primary_database() -> AsyncGenerator[URL]:
    name = f"test-primary_database-{uuid4()}"

    url = URL.create(
        drivername="postgresql+asyncpg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        database=name,
    )

    await create_database(url)

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, partial(run_alembic_upgrade_head, url),
    )

    # Seed reference data into template
    await _seed_template(url)

    yield url

    await drop_database(url)


@pytest.fixture
async def database(
    primary_database: URL,
    testrun_uid: str,
) -> AsyncGenerator[URL]:
    """Fresh database per test, cloned from seeded template."""

    name = f"test-{uuid4()}-{testrun_uid}"

    url = URL.create(
        drivername=primary_database.drivername,
        username=primary_database.username,
        password=primary_database.password,
        host=primary_database.host,
        port=primary_database.port,
        database=name,
    )

    await create_database(url, template=primary_database.database)
    yield url
    await drop_database(url)


@pytest.fixture
async def database_sessionmaker(
    database: URL,
) -> AsyncGenerator[async_sessionmaker]:
    engine = create_async_engine(
        url=database,
        echo=False,
        poolclass=NullPool,
    )

    yield async_sessionmaker(bind=engine)

    await engine.dispose()


async def create_database(
    url: URL,
    *,
    encoding="utf8",
    template=None,
) -> None:
    database = url.database
    url = url._replace(database="postgres")

    engine = create_async_engine(
        url, isolation_level="AUTOCOMMIT", poolclass=NullPool,
    )

    if template is None:
        template = "template1"

    try:
        async with engine.begin() as conn:
            stmt = text(
                f'CREATE DATABASE "{database}" '
                f"ENCODING '{encoding}' "
                f'TEMPLATE "{template}"'
            )
            await conn.execute(stmt)
    finally:
        await engine.dispose()


async def drop_database(url: URL) -> None:
    database = url.database
    url = url._replace(database="postgres")

    engine = create_async_engine(
        url, isolation_level="AUTOCOMMIT", poolclass=NullPool,
    )

    try:
        async with engine.begin() as conn:
            stmt = text(f'DROP DATABASE "{database}"')
            await conn.execute(stmt)
    finally:
        await engine.dispose()
```

Key changes:
- `primary_database` now calls `_seed_template()` after migrations
- `database` is **function-scoped** (was class-scoped)
- `database_sessionmaker` is **function-scoped** (follows database)
- `database` teardown now drops the DB (was commented out)

- [ ] **Step 2: Verify fixture loads**

Run: `pytest tests/babycli/test_utils.py -v --no-header -q`
Expected: passes (babycli tests don't use DB fixtures)

- [ ] **Step 3: Commit**

```bash
git add tests/fixtures/database.py
git commit -m "refactor(tests): function-scoped DB with seeded template"
```

---

## Task 2: Session-scoped app with per-test DB swap

**Files:**
- Modify: `tests/fixtures/app.py`

- [ ] **Step 1: Rewrite `tests/fixtures/app.py`**

```python
# tests/fixtures/app.py
from collections.abc import AsyncGenerator

import pytest
import sqlalchemy
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from babytroc.app import create_app
from babytroc.infrastructure.config import (
    Config,
    DatabaseConfig,
    PubsubConfig,
    RedisConfig,
    S3Config,
)
from babytroc.infrastructure.database import (
    create_session_maker,
    init_db_session_dependency,
)


@pytest.fixture(scope="session")
async def app_config(
    primary_database: sqlalchemy.URL,
    worker_id: str,
) -> Config:
    """App config — session-scoped, one per worker."""

    if worker_id == "master":
        redis_db = 3
    else:
        redis_db = 3 + int(worker_id.replace("gw", ""))

    redis_config = RedisConfig.from_env(db=redis_db)

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


@pytest.fixture(scope="session")
async def app(
    app_config: Config,
    worker_id: str,
) -> AsyncGenerator[FastAPI]:
    """One FastAPI app per xdist worker."""
    prefix = f"worker-{worker_id}:"
    app = create_app(app_config, pubsub_channel_prefix=prefix)
    async with LifespanManager(app):
        yield app


@pytest.fixture(autouse=True)
async def _swap_app_db(
    app: FastAPI,
    database_sessionmaker,
):
    """Swap app's DB session maker to point at this test's fresh DB."""
    init_db_session_dependency(database_sessionmaker)
    yield


@pytest.fixture(autouse=True)
async def _flush_redis(app: FastAPI):
    """Flush Redis between tests."""
    await app.state.redis.flushdb()
    yield
    await app.state.redis.flushdb()
```

Key changes:
- `app_config` → session-scoped (was class-scoped), uses `primary_database`
- `app` → session-scoped (was class-scoped), uses worker ID for pubsub prefix
- `_swap_app_db` — new autouse function-scoped fixture, swaps DB per test
- `_flush_redis` — function-scoped autouse (was class-scoped `flush_redis_cache`)

- [ ] **Step 2: Commit**

```bash
git add tests/fixtures/app.py
git commit -m "refactor(tests): session-scoped app with per-test DB swap"
```

---

## Task 3: Function-scoped user, region, category, image fixtures

**Files:**
- Modify: `tests/fixtures/users.py`
- Modify: `tests/fixtures/regions.py`
- Modify: `tests/fixtures/categories.py`
- Modify: `tests/fixtures/items.py`

- [ ] **Step 1: Rewrite `tests/fixtures/users.py`**

Users are pre-seeded in template. Fixtures now SELECT instead of INSERT.

```python
# tests/fixtures/users.py
import random
from string import ascii_letters
from typing import TypedDict

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.user import services as user_services
from babytroc.domains.user.schemas.create import UserCreate
from babytroc.domains.user.schemas.private import UserPrivateRead
from babytroc.shared.hash import HashedStr


class UserData(TypedDict):
    name: str
    email: str
    password: str


@pytest.fixture(scope="session")
def alice_user_data() -> UserData:
    return {
        "name": "alice",
        "email": "alice@babytroc.ch",
        "password": "password-Alice-42",
    }


@pytest.fixture(scope="session")
def bob_user_data() -> UserData:
    return {
        "name": "bob",
        "email": "bob@babytroc.ch",
        "password": "password-Bob-42",
    }


@pytest.fixture(scope="session")
def carol_user_data() -> UserData:
    return {
        "name": "carol",
        "email": "carol@babytroc.ch",
        "password": "password-Carol-42",
    }


@pytest.fixture
async def alice(
    database_sessionmaker: async_sessionmaker,
) -> UserPrivateRead:
    """Read pre-seeded Alice from template DB."""
    async with database_sessionmaker.begin() as session:
        return await user_services.get_user_by_email_private(
            session, "alice@babytroc.ch",
        )


@pytest.fixture
async def bob(
    database_sessionmaker: async_sessionmaker,
) -> UserPrivateRead:
    """Read pre-seeded Bob from template DB."""
    async with database_sessionmaker.begin() as session:
        return await user_services.get_user_by_email_private(
            session, "bob@babytroc.ch",
        )


@pytest.fixture
async def carol(
    database_sessionmaker: async_sessionmaker,
) -> UserPrivateRead:
    """Read pre-seeded Carol from template DB."""
    async with database_sessionmaker.begin() as session:
        return await user_services.get_user_by_email_private(
            session, "carol@babytroc.ch",
        )


def random_str(length: int) -> str:
    return "".join(random.choices(ascii_letters, k=length))


@pytest.fixture
async def many_users(
    database_sessionmaker: async_sessionmaker,
) -> list[UserPrivateRead]:
    """Many users — created per test (heavy)."""

    n = 256
    random.seed(0x538D)

    password_hash = HashedStr("xyzXYZ123")

    user_creates = [
        UserCreate(
            name=random_str(8),
            email=f"{random_str(8)}@{random_str(8)}.com",
            password=password_hash,
        )
        for _ in range(n)
    ]

    async with database_sessionmaker.begin() as session:
        return await user_services.create_many_users_without_validation(
            session,
            user_creates=user_creates,
            validated=True,
        )
```

Key changes:
- `*_user_data` → session-scoped (constants, no DB dep)
- `alice/bob/carol` → function-scoped, use `get_user_by_email_private` (SELECT)
- `many_users` → function-scoped (was class-scoped), creates per test

- [ ] **Step 2: Rewrite `tests/fixtures/regions.py`**

```python
# tests/fixtures/regions.py
from typing import TypedDict

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.region import services as region_services
from babytroc.domains.region.schemas.read import RegionRead
from babytroc.infrastructure.cache_client import NullCache


class RegionData(TypedDict):
    id: int
    name: str


@pytest.fixture(scope="session")
def regions_data() -> list[RegionData]:
    return [
        {"id": 1, "name": "region1"},
        {"id": 2, "name": "region2"},
    ]


@pytest.fixture
async def regions(
    database_sessionmaker: async_sessionmaker,
) -> list[RegionRead]:
    """Read pre-seeded regions from template DB."""
    async with database_sessionmaker.begin() as session:
        return await region_services.list_regions(
            session, NullCache(),
        )
```

- [ ] **Step 3: Rewrite `tests/fixtures/categories.py`**

```python
# tests/fixtures/categories.py
import random

import pytest
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.category import services as category_services
from babytroc.domains.category.schemas.read import CategoryRead
from babytroc.domains.item.models.category import ItemCategoryAssociation
from babytroc.domains.item.schemas.read import ItemRead
from babytroc.infrastructure.cache_client import NullCache


@pytest.fixture
async def categories(
    database_sessionmaker: async_sessionmaker,
) -> list[CategoryRead]:
    """Read pre-seeded categories from template DB."""
    async with database_sessionmaker.begin() as session:
        return await category_services.list_categories(
            session, NullCache(),
        )


@pytest.fixture
async def alice_items_with_categories(
    database_sessionmaker: async_sessionmaker,
    alice_many_items: list[ItemRead],
    categories: list[CategoryRead],
) -> list[ItemRead]:
    """Assign 1-3 random categories to each of Alice's many items."""

    random.seed(0xCAFE)

    child_categories = [
        cat for cat in categories if cat.parent_slug is not None
    ]
    associations = []

    for item in alice_many_items:
        chosen = random.sample(
            child_categories,
            k=random.randint(1, min(3, len(child_categories))),
        )
        for cat in chosen:
            associations.append(
                {"item_id": item.id, "category_slug": cat.slug},
            )

    async with database_sessionmaker.begin() as session:
        await session.execute(
            insert(ItemCategoryAssociation).values(associations),
        )

    from babytroc.domains.item.services import get_many_items

    async with database_sessionmaker() as session:
        return await get_many_items(
            db=session,
            item_ids={item.id for item in alice_many_items},
        )
```

- [ ] **Step 4: Rewrite `tests/fixtures/items.py`**

Image data fixtures → session-scoped (pure data). Image upload fixtures → function-scoped (read from pre-seeded DB). Item data fixtures → function-scoped (depend on images). Item creation fixtures → function-scoped (already were or need to be).

```python
# tests/fixtures/items.py
import random
from io import BytesIO
from typing import TypedDict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.image import services as image_services
from babytroc.domains.item.models.image import ItemImage
from babytroc.domains.image.schemas.read import ItemImageRead
from babytroc.domains.item import services as item_services
from babytroc.domains.item.schemas.base import MonthRange
from babytroc.domains.item.schemas.create import ItemCreate
from babytroc.domains.item.schemas.read import ItemRead
from babytroc.domains.region.schemas.read import RegionRead
from babytroc.domains.user.schemas.private import UserPrivateRead
from babytroc.infrastructure.config import Config
from tests.utils import random_sample, random_str, random_targeted_age_months


class UserData(TypedDict):
    name: str
    email: str
    password: str


class ItemData(TypedDict):
    name: str
    description: str
    targeted_age_months: str
    regions: list[int]
    images: list[str]


# --- Image data (pure bytes, no DB) ---

@pytest.fixture(scope="session")
def alice_items_image_data() -> bytes:
    return "P1\n3 3\n101\n101\n010".encode()


@pytest.fixture(scope="session")
def alice_new_item_image_data() -> bytes:
    return "P1\n3 3\n000\n111\n000".encode()


@pytest.fixture(scope="session")
def alice_special_item_image_data() -> bytes:
    return "P1\n3 3\n101\n111\n010".encode()


@pytest.fixture(scope="session")
def bob_items_image_data() -> bytes:
    return "P1\n3 3\n101\n101\n010".encode()


# --- Image fixtures (read pre-seeded from template) ---

@pytest.fixture
async def alice_items_image(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> ItemImageRead:
    """Alice's item image (pre-seeded, image #1)."""
    async with database_sessionmaker.begin() as session:
        row = (
            await session.execute(
                select(ItemImage)
                .where(ItemImage.owner_id == alice.id)
                .order_by(ItemImage.name)
                .limit(1)
            )
        ).scalar_one()
        return ItemImageRead.model_validate(row)


@pytest.fixture
async def alice_new_item_images(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[ItemImageRead]:
    """Alice's new item images (pre-seeded, images #2-4)."""
    async with database_sessionmaker.begin() as session:
        rows = (
            await session.execute(
                select(ItemImage)
                .where(ItemImage.owner_id == alice.id)
                .order_by(ItemImage.name)
                .offset(1)
                .limit(3)
            )
        ).scalars().all()
        return [ItemImageRead.model_validate(r) for r in rows]


@pytest.fixture
async def alice_special_item_images(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[ItemImageRead]:
    """Alice's special item images (pre-seeded, images #5-6)."""
    async with database_sessionmaker.begin() as session:
        rows = (
            await session.execute(
                select(ItemImage)
                .where(ItemImage.owner_id == alice.id)
                .order_by(ItemImage.name)
                .offset(4)
                .limit(2)
            )
        ).scalars().all()
        return [ItemImageRead.model_validate(r) for r in rows]


@pytest.fixture
async def bob_items_image(
    database_sessionmaker: async_sessionmaker,
    bob: UserPrivateRead,
) -> ItemImageRead:
    """Bob's item image (pre-seeded)."""
    async with database_sessionmaker.begin() as session:
        row = (
            await session.execute(
                select(ItemImage)
                .where(ItemImage.owner_id == bob.id)
                .order_by(ItemImage.name)
                .limit(1)
            )
        ).scalar_one()
        return ItemImageRead.model_validate(row)


# --- Item data fixtures ---

@pytest.fixture
async def alice_items_data(
    alice_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemData]:
    return [
        {
            "name": "candle",
            "description": "dwell into a flowerbed",
            "targeted_age_months": "4-10",
            "regions": [regions[0].id],
            "images": [alice_items_image.name],
        },
    ]


@pytest.fixture
async def alice_new_item_data(
    alice_new_item_images: list[ItemImageRead],
    regions: list[RegionRead],
) -> ItemData:
    return {
        "name": "new-item",
        "description": "This is the latest new item created by alice.",
        "targeted_age_months": "7-",
        "regions": [regions[1].id],
        "images": [image.name for image in alice_new_item_images],
    }


@pytest.fixture
async def alice_special_item_data(
    alice_special_item_images: list[ItemImageRead],
    regions: list[RegionRead],
) -> ItemData:
    return {
        "name": "Special item",
        "description": "This is the special item created by alice.",
        "targeted_age_months": "2-5",
        "regions": [regions[0].id],
        "images": [
            image.name for image in alice_special_item_images
        ],
    }


@pytest.fixture
async def bob_items_data(
    bob_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemData]:
    return [
        {
            "name": "Dark side",
            "description": (
                "Breathe, breathe in the air. "
                "Don't be afraid to care"
            ),
            "targeted_age_months": "16-",
            "regions": [regions[0].id, regions[1].id],
            "images": [bob_items_image.name],
        },
    ]


# --- Item creation fixtures ---

@pytest.fixture
async def alice_items(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    alice_items_data: list[ItemData],
) -> list[ItemRead]:
    async with database_sessionmaker.begin() as session:
        return [
            await item_services.create_item(
                db=session,
                owner_id=alice.id,
                item_create=ItemCreate(
                    name=item["name"],
                    description=item["description"],
                    images=item["images"],
                    targeted_age_months=MonthRange(
                        item["targeted_age_months"],
                    ),
                    regions=set(item["regions"]),
                ),
            )
            for item in alice_items_data
        ]


@pytest.fixture
async def alice_new_item(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    alice_new_item_data: ItemData,
) -> ItemRead:
    async with database_sessionmaker.begin() as session:
        return await item_services.create_item(
            db=session,
            owner_id=alice.id,
            item_create=ItemCreate(
                name=alice_new_item_data["name"],
                description=alice_new_item_data["description"],
                images=alice_new_item_data["images"],
                targeted_age_months=MonthRange(
                    alice_new_item_data["targeted_age_months"],
                ),
                regions=set(alice_new_item_data["regions"]),
            ),
        )


@pytest.fixture
async def alice_special_item(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    alice_special_item_data: ItemData,
) -> ItemRead:
    async with database_sessionmaker.begin() as session:
        return await item_services.create_item(
            db=session,
            owner_id=alice.id,
            item_create=ItemCreate(
                name=alice_special_item_data["name"],
                description=alice_special_item_data["description"],
                images=alice_special_item_data["images"],
                targeted_age_months=MonthRange(
                    alice_special_item_data[
                        "targeted_age_months"
                    ],
                ),
                regions=set(
                    alice_special_item_data["regions"],
                ),
            ),
        )


@pytest.fixture
async def alice_many_items(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    alice_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemRead]:
    n = 256
    random.seed(0x25D4)

    async with database_sessionmaker.begin() as session:
        return await item_services.create_many_items(
            db=session,
            items=[
                item_services.create.CreateItem(
                    owner_id=alice.id,
                    item_create=ItemCreate(
                        name=random_str(8),
                        description=random_str(50),
                        targeted_age_months=random_targeted_age_months(),
                        regions=set(
                            random_sample(
                                [reg.id for reg in regions],
                            ),
                        ),
                        images=[alice_items_image.name],
                        blocked=False,
                    ),
                )
                for _ in range(n)
            ],
        )


@pytest.fixture
async def bob_items(
    database_sessionmaker: async_sessionmaker,
    bob: UserPrivateRead,
    bob_items_data: list[ItemData],
) -> list[ItemRead]:
    async with database_sessionmaker.begin() as session:
        return [
            await item_services.create_item(
                db=session,
                owner_id=bob.id,
                item_create=ItemCreate(
                    name=item["name"],
                    description=item["description"],
                    images=item["images"],
                    targeted_age_months=MonthRange(
                        item["targeted_age_months"],
                    ),
                    regions=set(item["regions"]),
                ),
            )
            for item in bob_items_data
        ]


@pytest.fixture
async def items(
    alice_items: list[ItemRead],
    bob_items: list[ItemRead],
) -> list[ItemRead]:
    return [*alice_items, *bob_items]


@pytest.fixture
async def many_items(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    bob: UserPrivateRead,
    alice_items_image: ItemImageRead,
    bob_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemRead]:
    n = 256
    random.seed(0xBDF81829)

    owner_ids, images = [
        list(column)
        for column in zip(
            *random.choices(
                [
                    (alice.id, alice_items_image),
                    (bob.id, bob_items_image),
                ],
                k=n,
            ),
            strict=True,
        )
    ]

    async with database_sessionmaker.begin() as session:
        return await item_services.create_many_items(
            db=session,
            items=[
                item_services.create.CreateItem(
                    owner_id=owner_id,
                    item_create=ItemCreate(
                        name=random_str(8),
                        description=random_str(50),
                        targeted_age_months=random_targeted_age_months(),
                        regions=set(
                            random_sample(
                                [reg.id for reg in regions],
                            ),
                        ),
                        images=[image.name],
                        blocked=random.choice(
                            [False] * 3 + [True],
                        ),
                    ),
                )
                for owner_id, image in zip(
                    owner_ids, images, strict=True,
                )
            ],
        )


@pytest.fixture(scope="session")
def some_item_french_names() -> list[str]:
    random.seed(0xA19F)
    return [
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
        *(
            f"{random_str(5)} bleu {random_str(5)}"
            for _ in range(40)
        ),
    ]


@pytest.fixture
async def some_items_with_french_names(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    bob: UserPrivateRead,
    alice_items_image: ItemImageRead,
    bob_items_image: ItemImageRead,
    regions: list[RegionRead],
    some_item_french_names: list[str],
) -> list[ItemRead]:
    random.seed(0x15976)

    owner_ids, images = [
        list(column)
        for column in zip(
            *random.choices(
                [
                    (alice.id, alice_items_image),
                    (bob.id, bob_items_image),
                ],
                k=len(some_item_french_names),
            ),
            strict=True,
        )
    ]

    async with database_sessionmaker.begin() as session:
        return await item_services.create_many_items(
            db=session,
            items=[
                item_services.create.CreateItem(
                    owner_id=owner_id,
                    item_create=ItemCreate(
                        name=name,
                        description=random_str(50),
                        targeted_age_months=random_targeted_age_months(),
                        regions=set(
                            random_sample(
                                [reg.id for reg in regions],
                            ),
                        ),
                        images=[image.name],
                        blocked=random.choice(
                            [False] * 3 + [True],
                        ),
                    ),
                )
                for name, owner_id, image in zip(
                    some_item_french_names,
                    owner_ids,
                    images,
                    strict=True,
                )
            ],
        )
```

Key changes from current: ALL fixtures are function-scoped (no `scope="class"`). Image data fixtures are session-scoped (pure bytes). Image upload fixtures read pre-seeded images by position.

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/users.py tests/fixtures/regions.py tests/fixtures/categories.py tests/fixtures/items.py
git commit -m "refactor(tests): function-scoped user/region/category/item fixtures"
```

---

## Task 4: Function-scoped loan and chat fixtures

**Files:**
- Modify: `tests/fixtures/loans.py`
- Modify: `tests/fixtures/chat.py`

- [ ] **Step 1: Update `tests/fixtures/loans.py`**

Remove `scope="class"` from all fixtures. The heavy fixtures (`many_loan_requests_for_alice_items`, `many_loan_requests_for_alice_special_item`, `alice_many_loans`) become function-scoped. They will be overridden to class-scoped in heavy test conftest files.

Open the file and remove every `scope="class"` annotation. The function-scoped fixtures (no scope arg) stay unchanged. Specifically, change lines:
- Line 136: `@pytest.fixture(scope="class")` → `@pytest.fixture`
- Line 275: `@pytest.fixture(scope="class")` → `@pytest.fixture`
- Line 397: `@pytest.fixture(scope="class")` → `@pytest.fixture`

- [ ] **Step 2: Update `tests/fixtures/chat.py`**

Remove `scope="class"` from:
- Line 148: `@pytest.fixture(scope="class")` → `@pytest.fixture(scope="session")` (pure data, no DB)
- Line 194: `@pytest.fixture(scope="class")` → `@pytest.fixture`

For `alice_many_messages_to_bob_text` (line 148) — this is pure data, make it session-scoped.

- [ ] **Step 3: Commit**

```bash
git add tests/fixtures/loans.py tests/fixtures/chat.py
git commit -m "refactor(tests): function-scoped loan and chat fixtures"
```

---

## Task 5: Class-scoped overrides for heavy test directories

**Files:**
- Create: `tests/item/conftest.py`
- Create: `tests/loan/conftest.py`
- Create: `tests/chat/conftest.py`

Heavy test files need class-scoped DB to avoid recreating 256+ items per test. Create conftest.py in each directory to override `database` and `database_sessionmaker` back to class-scoped.

- [ ] **Step 1: Create `tests/item/conftest.py`**

```python
# tests/item/conftest.py
"""Override database to class-scoped for heavy pagination tests."""

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from tests.fixtures.database import create_database, drop_database


@pytest.fixture(scope="class")
async def database(
    primary_database: URL,
    testrun_uid: str,
) -> AsyncGenerator[URL]:
    name = f"test-{uuid4()}-{testrun_uid}"
    url = URL.create(
        drivername=primary_database.drivername,
        username=primary_database.username,
        password=primary_database.password,
        host=primary_database.host,
        port=primary_database.port,
        database=name,
    )
    await create_database(url, template=primary_database.database)
    yield url
    await drop_database(url)


@pytest.fixture(scope="class")
async def database_sessionmaker(
    database: URL,
) -> AsyncGenerator[async_sessionmaker]:
    engine = create_async_engine(
        url=database, echo=False, poolclass=NullPool,
    )
    yield async_sessionmaker(bind=engine)
    await engine.dispose()
```

- [ ] **Step 2: Create `tests/loan/conftest.py`**

Same content as `tests/item/conftest.py`:

```python
# tests/loan/conftest.py
"""Override database to class-scoped for heavy pagination tests."""

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from tests.fixtures.database import create_database, drop_database


@pytest.fixture(scope="class")
async def database(
    primary_database: URL,
    testrun_uid: str,
) -> AsyncGenerator[URL]:
    name = f"test-{uuid4()}-{testrun_uid}"
    url = URL.create(
        drivername=primary_database.drivername,
        username=primary_database.username,
        password=primary_database.password,
        host=primary_database.host,
        port=primary_database.port,
        database=name,
    )
    await create_database(url, template=primary_database.database)
    yield url
    await drop_database(url)


@pytest.fixture(scope="class")
async def database_sessionmaker(
    database: URL,
) -> AsyncGenerator[async_sessionmaker]:
    engine = create_async_engine(
        url=database, echo=False, poolclass=NullPool,
    )
    yield async_sessionmaker(bind=engine)
    await engine.dispose()
```

- [ ] **Step 3: Create `tests/chat/conftest.py`**

Same pattern:

```python
# tests/chat/conftest.py
"""Override database to class-scoped for heavy chat tests."""

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from tests.fixtures.database import create_database, drop_database


@pytest.fixture(scope="class")
async def database(
    primary_database: URL,
    testrun_uid: str,
) -> AsyncGenerator[URL]:
    name = f"test-{uuid4()}-{testrun_uid}"
    url = URL.create(
        drivername=primary_database.drivername,
        username=primary_database.username,
        password=primary_database.password,
        host=primary_database.host,
        port=primary_database.port,
        database=name,
    )
    await create_database(url, template=primary_database.database)
    yield url
    await drop_database(url)


@pytest.fixture(scope="class")
async def database_sessionmaker(
    database: URL,
) -> AsyncGenerator[async_sessionmaker]:
    engine = create_async_engine(
        url=database, echo=False, poolclass=NullPool,
    )
    yield async_sessionmaker(bind=engine)
    await engine.dispose()
```

- [ ] **Step 4: Commit**

```bash
git add tests/item/conftest.py tests/loan/conftest.py tests/chat/conftest.py
git commit -m "refactor(tests): class-scoped DB overrides for heavy test dirs"
```

---

## Task 6: Run full test suite and fix issues

**Files:** any that need fixing

- [ ] **Step 1: Run babycli tests (should pass unaffected)**

Run: `pytest tests/babycli/ -v --no-header -q`
Expected: 28 passed

- [ ] **Step 2: Run a light test file**

Run: `pytest tests/test_auth.py -v --no-header -q`
Expected: passes with function-scoped DB

- [ ] **Step 3: Run a heavy test file**

Run: `pytest tests/item/test_item_read.py -v --no-header -q`
Expected: passes with class-scoped DB override

- [ ] **Step 4: Run chat tests**

Run: `pytest tests/chat/ -v --no-header -q`
Expected: passes

- [ ] **Step 5: Run full suite**

Run: `pytest -n logical --dist loadfile --maxfail=3`
Expected: all tests pass, no flaky 404s

- [ ] **Step 6: Fix any issues found, commit**

```bash
git add -u
git commit -m "fix(tests): resolve test isolation issues"
```

- [ ] **Step 7: Run full suite again to confirm stability**

Run: `pytest -n logical --dist loadfile --maxfail=1`
Run it 3 times. Should pass every time.

- [ ] **Step 8: Final commit**

```bash
git commit -m "refactor(tests): complete test isolation redesign"
```
