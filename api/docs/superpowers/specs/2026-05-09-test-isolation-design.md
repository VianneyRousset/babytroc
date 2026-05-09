# Test Isolation Redesign

**Date:** 2026-05-09
**Status:** Approved

## Problem

Tests share class-scoped databases. Under parallel execution, function-scoped fixtures (items, loans) create data within the shared DB. Timing issues cause flaky 404s when one test's HTTP request can't see another test's fixture data.

## Goal

Per-function database isolation. Every test gets a fresh DB clone. No shared mutable state between tests.

## Architecture

### Scope Hierarchy

```
Session scope (once per xdist worker):
  primary_database    — CREATE DB + alembic + seed reference data
  app                 — one FastAPI instance per worker
  broadcast           — Redis pubsub with worker-level channel prefix

Function scope (every test):
  database            — CREATE DB ... TEMPLATE primary_database
  database_sessionmaker — engine bound to fresh DB
  _swap_app_db        — autouse, swaps app's session maker to fresh DB
  _flush_redis        — autouse, flushes worker's Redis DB
  alice/bob/carol     — SELECT from pre-seeded template (no INSERT)
  clients             — login via HTTP
  websockets          — connect/disconnect
  items/loans/chats   — test-specific data
```

### Template Database

`primary_database` (session-scoped) runs migrations then seeds shared reference data:

- 3 users: alice, bob, carol (with known passwords, validated=True)
- Regions from fixture data
- Categories from fixture data
- Images uploaded for alice (3 new_item + 2 special_item) and bob (1 image)

This data is identical across all tests. Baking it into the template avoids re-creating it per test.

### Per-Function Database

Each test clones from template:

```python
@pytest.fixture
async def database(primary_database: URL, testrun_uid: str) -> AsyncGenerator[URL]:
    name = f"test-{uuid4()}-{testrun_uid}"
    url = primary_database._replace(database=name)
    await create_database(url, template=primary_database.database)
    yield url
    await drop_database(url)
```

Cost: ~100ms per `CREATE DATABASE ... TEMPLATE`. With 309 tests across 8 workers, ~4s wall clock overhead.

### Worker-Scoped App

One FastAPI app per xdist worker. Session maker swapped per test via autouse fixture:

```python
@pytest.fixture(autouse=True)
async def _swap_app_db(app, database_sessionmaker):
    init_db_session_dependency(database_sessionmaker)
    yield
```

No lifespan overhead per test. App created once, DB connection swapped.

### Redis Isolation

Each worker gets its own Redis DB (existing: `3 + worker_index`). Pubsub channel prefix set per worker at app creation. Autouse fixture flushes Redis DB between tests:

```python
@pytest.fixture(autouse=True)
async def _flush_redis(app):
    await app.state.redis.flushdb()
    yield
    await app.state.redis.flushdb()
```

Tests on same worker run sequentially (xdist guarantee). Function-scoped websocket disconnect + Redis flush prevents message leaking.

### User Fixtures

Current: class-scoped, INSERT users per class.
New: function-scoped, SELECT from pre-seeded template.

```python
@pytest.fixture
async def alice(database_sessionmaker) -> UserPrivateRead:
    async with database_sessionmaker.begin() as session:
        return await user_services.get_user_by_name(session, "alice")
```

User data fixtures (`alice_user_data`, etc.) become session-scoped constants — no DB dependency.

### Other Fixtures

All fixtures depending on `database` or `database_sessionmaker` become function-scoped:

- `regions`, `categories` — SELECT from template (no INSERT)
- `alice_new_item_images`, `alice_special_item_images`, `bob_items_image` — SELECT from template
- `alice_new_item`, `alice_special_item` — function-scoped INSERT (test-specific)
- All loan/chat fixtures — function-scoped INSERT (test-specific, already function-scoped)
- `clients` — function-scoped (already)
- `websockets` — function-scoped (already)

### Items/Images Strategy

Images are seeded into `primary_database`. But items are NOT seeded — they're test-specific. Images exist in the template; tests create items referencing those images.

Current `alice_new_item_images` fixture uploads images. New version reads pre-seeded images:

```python
@pytest.fixture
async def alice_new_item_images(database_sessionmaker, alice) -> list[ItemImageRead]:
    async with database_sessionmaker.begin() as session:
        return await image_services.list_images_by_owner(session, owner_id=alice.id)
```

Or keep uploading per test if `list_images_by_owner` doesn't exist — the overhead is small (~50ms for 3 images).

### S3 Isolation

S3 (MinIO) bucket is shared. Images uploaded in template seeding persist. Tests creating new items upload new images — these accumulate but don't conflict (unique names). No cleanup needed per test.

## Changes Summary

| File | Change |
|------|--------|
| `tests/fixtures/database.py` | `database` → function-scoped. `primary_database` seeds reference data. Drop cleanup is now per-function. |
| `tests/fixtures/app.py` | `app`, `app_config` → session-scoped. Add `_swap_app_db` autouse. `flush_redis_cache` → function-scoped. Pubsub prefix uses worker ID. |
| `tests/fixtures/users.py` | `alice/bob/carol` → function-scoped SELECT. `*_user_data` → session-scoped constants. `many_users` stays class-scoped → must become function-scoped. |
| `tests/fixtures/regions.py` | `regions` → function-scoped SELECT from template. |
| `tests/fixtures/categories.py` | `categories` → function-scoped SELECT from template. |
| `tests/fixtures/items.py` | Image fixtures → function-scoped (read from template or re-upload). Item data/creation fixtures stay function-scoped. Class-scoped item fixtures (`alice_special_item`, `many_items`, etc.) → function-scoped. |
| `tests/fixtures/loans.py` | Class-scoped loan fixtures (`many_loan_requests_*`, `many_loans_*`) → function-scoped. |
| `tests/fixtures/chat.py` | Class-scoped chat fixtures → function-scoped. |
| `tests/fixtures/clients.py` | Already function-scoped. No change. |
| `tests/fixtures/websockets.py` | Already function-scoped. No change. |
| `pyproject.toml` | `addopts` remove `--dist loadfile` (no longer needed, any distribution works). |

## Estimated Performance

| Metric | Current | New |
|--------|---------|-----|
| DB creates | ~50 (one per class) | ~309 (one per test) |
| DB create cost | ~100ms each | ~100ms each |
| User/region/category setup | ~50 × ~200ms | 0 (template) |
| Total overhead | ~12s | ~31s DB creates, but 0 fixture setup |
| Net change | — | ~+15s distributed across 8 workers = ~2s wall clock |
| Suite time | ~90s | ~92s estimated |

## Success Criteria

- All 309 tests pass with `-n logical --dist loadfile`
- No flaky 404s under parallel load
- `pytest -n1` (single worker) also passes
- Suite time stays under 120s
- No class-scoped fixtures that depend on `database`
