# Redis Caching & Pub/Sub Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Redis-based service-layer caching and migrate real-time pub/sub from Postgres LISTEN/NOTIFY to Redis.

**Architecture:** Redis client + Cache abstraction injected via FastAPI dependencies. Service-layer cache-aside reads, explicit invalidation on writes. Broadcaster backend swapped from Postgres to Redis. Postgres `notify_chat_members_new_message` trigger removed; notifications published from service code.

**Tech Stack:** `redis[hiredis]`, `broadcaster[redis]`, Pydantic JSON serialization

**Spec:** `docs/superpowers/specs/2026-05-04-redis-caching-design.md`

---

### Task 1: Add Redis dependency and configuration

**Files:**
- Modify: `pyproject.toml`
- Modify: `app/config.py`
- Modify: `.env.yaml`

- [ ] **Step 1: Add `redis[hiredis]` to dependencies**

In `pyproject.toml`, add to the `dependencies` list:

```toml
"redis[hiredis]>=5.0.0",
```

- [ ] **Step 2: Replace `broadcaster[postgres]` with `broadcaster[redis]`**

In `pyproject.toml`, change:

```toml
"broadcaster[postgres] @ git+https://github.com/encode/broadcaster.git@6b3ea71d4f8fb038fa7d357a1fb3750d58ac614d",
```

to:

```toml
"broadcaster[redis] @ git+https://github.com/encode/broadcaster.git@6b3ea71d4f8fb038fa7d357a1fb3750d58ac614d",
```

- [ ] **Step 3: Add `RedisConfig` to `app/config.py`**

Add after `ImgpushConfig`:

```python
class RedisConfig(NamedTuple):
    host: str
    port: int
    db: int
    password: str | None

    @classmethod
    def from_env(
        cls,
        host: str | None = None,
        port: int | None = None,
        db: int | None = None,
        password: str | None = None,
    ) -> Self:
        if host is None:
            host = os.environ.get("REDIS_HOST", "localhost")
        if port is None:
            port = int(os.environ.get("REDIS_PORT", "6379"))
        if db is None:
            db = int(os.environ.get("REDIS_DB", "0"))
        if password is None:
            password = os.environ.get("REDIS_PASSWORD")

        return cls(host=host, port=port, db=db, password=password)

    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"
```

- [ ] **Step 4: Update `PubsubConfig` to use Redis DSN**

Replace `PubsubConfig` entirely:

```python
class PubsubConfig(NamedTuple):
    url: str

    @classmethod
    def from_env(cls, url: str | None = None) -> Self:
        if url is None:
            redis_config = RedisConfig.from_env()
            url = redis_config.url

        return cls(url=url)
```

- [ ] **Step 5: Add `redis` field to `Config`**

In the `Config` NamedTuple, add `redis: RedisConfig` after `imgpush`:

```python
class Config(NamedTuple):
    host_name: str
    app_name: str
    test: bool
    delay: float
    database: DatabaseConfig
    pubsub: PubsubConfig
    email: EmailConfig
    imgpush: ImgpushConfig
    redis: RedisConfig
    auth: AuthConfig
```

In `Config.from_env()`, add the `redis` parameter and initialization:

```python
    @classmethod
    def from_env(
        cls,
        *,
        host_name: str | None = None,
        app_name: str | None = None,
        test: bool | None = None,
        delay: float | None = None,
        database: DatabaseConfig | None = None,
        pubsub: PubsubConfig | None = None,
        email: EmailConfig | None = None,
        imgpush: ImgpushConfig | None = None,
        redis: RedisConfig | None = None,
        auth: AuthConfig | None = None,
    ) -> Self:
        # ... existing code ...

        if redis is None:
            redis = RedisConfig.from_env()

        if pubsub is None:
            pubsub = PubsubConfig.from_env()

        # ... rest of existing code ...

        return cls(
            host_name=host_name,
            app_name=app_name,
            test=test,
            delay=delay,
            database=database,
            pubsub=pubsub,
            email=email,
            imgpush=imgpush,
            redis=redis,
            auth=auth,
        )
```

Note: `PubsubConfig.from_env()` now reads from `REDIS_*` env vars via `RedisConfig`, so ensure `redis` is initialized before `pubsub` in `Config.from_env()`.

- [ ] **Step 6: Add Redis env vars to `.env.yaml`**

```yaml
REDIS_HOST: "localhost"
REDIS_PORT: "6379"
REDIS_DB: "2"
```

- [ ] **Step 7: Install dependencies**

Run: `uv sync`

- [ ] **Step 8: Run lint**

Run: `mise run lint`
Expected: PASS (no lint errors from config changes)

- [ ] **Step 9: Commit**

```bash
git add pyproject.toml uv.lock app/config.py .env.yaml
git commit -m "feat: add Redis config and dependency, switch broadcaster to redis backend"
```

---

### Task 2: Create Redis client and Cache abstraction

**Files:**
- Create: `app/clients/redis.py`
- Create: `app/clients/cache.py`

- [ ] **Step 1: Write test for Cache abstraction**

Create `tests/test_cache.py`:

```python
import pytest
from redis.asyncio import Redis

from app.clients.cache import Cache


@pytest.fixture
async def redis_client():
    client = Redis(host="localhost", port=6379, db=3)
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.fixture
def cache(redis_client):
    return Cache(redis_client)


class TestCache:
    async def test_get_miss(self, cache):
        result = await cache.get("babytroc:test:miss")
        assert result is None

    async def test_set_and_get(self, cache):
        await cache.set("babytroc:test:key", '{"a": 1}', ttl=60)
        result = await cache.get("babytroc:test:key")
        assert result == b'{"a": 1}'

    async def test_delete(self, cache):
        await cache.set("babytroc:test:del", "value", ttl=60)
        await cache.delete("babytroc:test:del")
        result = await cache.get("babytroc:test:del")
        assert result is None

    async def test_delete_multiple(self, cache):
        await cache.set("babytroc:test:a", "1", ttl=60)
        await cache.set("babytroc:test:b", "2", ttl=60)
        await cache.delete("babytroc:test:a", "babytroc:test:b")
        assert await cache.get("babytroc:test:a") is None
        assert await cache.get("babytroc:test:b") is None

    async def test_delete_pattern(self, cache):
        await cache.set("babytroc:test:pattern:1", "a", ttl=60)
        await cache.set("babytroc:test:pattern:2", "b", ttl=60)
        await cache.set("babytroc:test:other", "c", ttl=60)
        await cache.delete_pattern("babytroc:test:pattern:*")
        assert await cache.get("babytroc:test:pattern:1") is None
        assert await cache.get("babytroc:test:pattern:2") is None
        assert await cache.get("babytroc:test:other") == b"c"

    async def test_get_or_set_miss(self, cache):
        async def factory():
            return '{"computed": true}'

        result = await cache.get_or_set("babytroc:test:factory", ttl=60, factory=factory)
        assert result == '{"computed": true}'
        assert await cache.get("babytroc:test:factory") == b'{"computed": true}'

    async def test_get_or_set_hit(self, cache):
        await cache.set("babytroc:test:cached", '{"cached": true}', ttl=60)

        async def factory():
            msg = "should not be called"
            raise AssertionError(msg)

        result = await cache.get_or_set("babytroc:test:cached", ttl=60, factory=factory)
        assert result == '{"cached": true}'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cache.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.clients.cache'`

- [ ] **Step 3: Create `app/clients/cache.py`**

```python
from collections.abc import Awaitable, Callable

from redis.asyncio import Redis


class Cache:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get(self, key: str) -> bytes | None:
        return await self._redis.get(key)

    async def set(self, key: str, value: str, ttl: int) -> None:
        await self._redis.set(key, value, ex=ttl)

    async def delete(self, *keys: str) -> None:
        if keys:
            await self._redis.delete(*keys)

    async def delete_pattern(self, pattern: str) -> None:
        cursor = 0
        while True:
            cursor, keys = await self._redis.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await self._redis.delete(*keys)
            if cursor == 0:
                break

    async def get_or_set(
        self,
        key: str,
        ttl: int,
        factory: Callable[[], Awaitable[str]],
    ) -> str:
        cached = await self.get(key)
        if cached is not None:
            return cached.decode()
        value = await factory()
        await self.set(key, value, ttl)
        return value
```

- [ ] **Step 4: Create `app/clients/redis.py`**

```python
from redis.asyncio import Redis

from app.config import RedisConfig


def create_redis_client(config: RedisConfig) -> Redis:
    return Redis(
        host=config.host,
        port=config.port,
        db=config.db,
        password=config.password,
    )
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_cache.py -v`
Expected: PASS

- [ ] **Step 6: Run lint**

Run: `mise run lint`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add app/clients/cache.py app/clients/redis.py tests/test_cache.py
git commit -m "feat: add Cache abstraction and Redis client factory"
```

---

### Task 3: Integrate Redis into app lifecycle and dependency injection

**Files:**
- Modify: `app/app.py`
- Create: `app/cache.py`
- Modify: `tests/fixtures/app.py`

- [ ] **Step 1: Create `app/cache.py` (dependency module, mirrors `app/email.py` pattern)**

```python
from app.clients.cache import Cache


def get_cache() -> Cache:
    return _cache


_cache: Cache


def init_cache_dependency(cache: Cache) -> None:
    global _cache
    _cache = cache
```

- [ ] **Step 2: Update `app/app.py` — add Redis and Cache initialization**

Add imports at top:

```python
from app.cache import init_cache_dependency
from app.clients.cache import Cache
from app.clients.redis import create_redis_client
```

Update `lifespan` to manage Redis lifecycle:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with app.state.broadcast:
        yield
    await app.state.redis.aclose()
```

In `create_app()`, after the broadcaster section, add:

```python
    # redis client and cache
    redis_client = create_redis_client(config.redis)
    app.state.redis = redis_client
    cache = Cache(redis_client)
    app.state.cache = cache
    init_cache_dependency(cache)
```

- [ ] **Step 3: Update broadcaster initialization in `create_app()`**

Change the broadcaster line from:

```python
    broadcast = Broadcast(config.pubsub.url.render_as_string(hide_password=False))
```

to:

```python
    broadcast = Broadcast(config.pubsub.url)
```

(Because `PubsubConfig.url` is now a plain `str` Redis URL, not a `sqlalchemy.URL`.)

- [ ] **Step 4: Update `tests/fixtures/app.py`**

Replace the `app_config` fixture to use Redis config:

```python
from collections.abc import AsyncGenerator

import pytest
import sqlalchemy
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from app.app import create_app
from app.config import Config, DatabaseConfig, PubsubConfig, RedisConfig


@pytest.fixture(scope="class")
async def app_config(
    database: sqlalchemy.URL,
) -> Config:
    """App config."""

    redis_config = RedisConfig.from_env(db=3)

    return Config.from_env(
        database=DatabaseConfig.from_env(
            url=database,
        ),
        pubsub=PubsubConfig(url=redis_config.url),
        redis=redis_config,
    )


@pytest.fixture(scope="class")
async def app(
    app_config: Config,
) -> AsyncGenerator[FastAPI]:
    app = create_app(app_config)
    async with LifespanManager(app):
        yield app
```

- [ ] **Step 5: Add Redis flush fixture to `tests/fixtures/app.py`**

Add after the `app` fixture:

```python
@pytest.fixture(autouse=True, scope="class")
async def flush_redis_cache(app: FastAPI):
    """Flush Redis test DB before each test class."""
    await app.state.redis.flushdb()
    yield
    await app.state.redis.flushdb()
```

- [ ] **Step 6: Run existing tests to verify nothing is broken**

Run: `mise run test`
Expected: PASS — all existing tests still work

- [ ] **Step 7: Run lint**

Run: `mise run lint`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add app/cache.py app/app.py tests/fixtures/app.py
git commit -m "feat: integrate Redis client and Cache into app lifecycle"
```

---

### Task 4: Add cache key helpers

**Files:**
- Create: `app/cache_keys.py`

- [ ] **Step 1: Write test for cache key hash**

Create `tests/test_cache_keys.py`:

```python
from app.cache_keys import cache_key_hash


class TestCacheKeyHash:
    def test_deterministic(self):
        h1 = cache_key_hash(a=1, b="hello")
        h2 = cache_key_hash(a=1, b="hello")
        assert h1 == h2

    def test_order_independent(self):
        h1 = cache_key_hash(b="hello", a=1)
        h2 = cache_key_hash(a=1, b="hello")
        assert h1 == h2

    def test_none_excluded(self):
        h1 = cache_key_hash(a=1)
        h2 = cache_key_hash(a=1, b=None)
        assert h1 == h2

    def test_different_values_different_hash(self):
        h1 = cache_key_hash(a=1)
        h2 = cache_key_hash(a=2)
        assert h1 != h2

    def test_length(self):
        h = cache_key_hash(a=1)
        assert len(h) == 16
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cache_keys.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Create `app/cache_keys.py`**

```python
import hashlib
import json

# --- TTL constants (seconds) ---
TTL_CATEGORIES = 86400  # 24h
TTL_REGIONS = 86400  # 24h
TTL_ITEM = 600  # 10min
TTL_ITEMS_LIST = 120  # 2min
TTL_USER = 1800  # 30min
TTL_USER_LIKED = 300  # 5min
TTL_USER_SAVED = 300  # 5min
TTL_USER_ITEMS = 300  # 5min
TTL_USER_CHATS = 120  # 2min
TTL_CHAT_MESSAGES = 120  # 2min
TTL_USER_LOANS = 300  # 5min
TTL_USER_BORROWINGS = 300  # 5min


def cache_key_hash(**params: object) -> str:
    filtered = {k: v for k, v in sorted(params.items()) if v is not None}
    raw = json.dumps(filtered, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# --- Key builders ---

def key_categories() -> str:
    return "babytroc:categories"


def key_regions() -> str:
    return "babytroc:regions"


def key_item(item_id: int) -> str:
    return f"babytroc:item:{item_id}"


def key_items_list(**query_params: object) -> str:
    return f"babytroc:items:list:{cache_key_hash(**query_params)}"


def key_user(user_id: int) -> str:
    return f"babytroc:user:{user_id}"


def key_user_liked_items(user_id: int) -> str:
    return f"babytroc:user:{user_id}:liked_items"


def key_user_saved_items(user_id: int) -> str:
    return f"babytroc:user:{user_id}:saved_items"


def key_user_chats(user_id: int) -> str:
    return f"babytroc:user:{user_id}:chats"


# --- Pattern builders (for invalidation) ---

def pattern_items_list() -> str:
    return "babytroc:items:list:*"


def pattern_user_items(user_id: int) -> str:
    return f"babytroc:user:{user_id}:items:*"


def pattern_user_loans(user_id: int) -> str:
    return f"babytroc:user:{user_id}:loans:*"


def pattern_user_borrowings(user_id: int) -> str:
    return f"babytroc:user:{user_id}:borrowings:*"


def pattern_chat_messages(item_id: int, borrower_id: int) -> str:
    return f"babytroc:chat:{item_id}_{borrower_id}:messages:*"


def pattern_user_all(user_id: int) -> str:
    return f"babytroc:user:{user_id}:*"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cache_keys.py -v`
Expected: PASS

- [ ] **Step 5: Run lint**

Run: `mise run lint`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add app/cache_keys.py tests/test_cache_keys.py
git commit -m "feat: add cache key builders and TTL constants"
```

---

### Task 5: Cache static data — categories and regions

**Files:**
- Modify: `app/services/category/read.py`
- Modify: `app/services/region/read.py`
- Modify: `app/routers/v1/utils.py`

- [ ] **Step 1: Write test for cached categories endpoint**

Create `tests/test_cache_static.py`:

```python
import pytest
from httpx import AsyncClient

from app.clients.cache import Cache


class TestCachedCategories:
    async def test_categories_cached_on_second_call(self, alice_client: AsyncClient, app):
        cache: Cache = app.state.cache

        # First call — cache miss
        r1 = await alice_client.get("/api/v1/categories")
        assert r1.status_code == 200
        categories = r1.json()

        # Verify cached
        cached = await cache.get("babytroc:categories")
        assert cached is not None

        # Second call — should return same data (from cache)
        r2 = await alice_client.get("/api/v1/categories")
        assert r2.status_code == 200
        assert r2.json() == categories


class TestCachedRegions:
    async def test_regions_cached_on_second_call(self, alice_client: AsyncClient, app):
        cache: Cache = app.state.cache

        r1 = await alice_client.get("/api/v1/regions")
        assert r1.status_code == 200
        regions = r1.json()

        cached = await cache.get("babytroc:regions")
        assert cached is not None

        r2 = await alice_client.get("/api/v1/regions")
        assert r2.status_code == 200
        assert r2.json() == regions
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cache_static.py -v`
Expected: FAIL — cache is empty after first call (not yet implemented)

- [ ] **Step 3: Update `app/services/category/read.py` to accept `Cache`**

Add caching to `list_categories`:

```python
from app.cache_keys import TTL_CATEGORIES, key_categories
from app.clients.cache import Cache
from app.schemas.category.read import CategoryRead


async def list_categories(db: AsyncSession, cache: Cache) -> list[CategoryRead]:
    cached = await cache.get(key_categories())
    if cached is not None:
        return [CategoryRead.model_validate(c) for c in json.loads(cached)]

    # existing query logic...
    stmt = ...
    result = (await db.execute(stmt)).unique().scalars().all()
    categories = [CategoryRead.model_validate(c) for c in result]

    await cache.set(
        key_categories(),
        json.dumps([c.model_dump() for c in categories], default=str),
        ttl=TTL_CATEGORIES,
    )

    return categories
```

Important: read the existing file first to preserve the exact query logic — only add the caching wrapper around it.

- [ ] **Step 4: Update `app/services/region/read.py` similarly**

Add caching to `list_regions` with the same pattern, using `key_regions()` and `TTL_REGIONS`.

- [ ] **Step 5: Update `app/routers/v1/utils.py` to pass `cache` to services**

```python
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.cache import get_cache
from app.clients.cache import Cache
from app.database import get_db_session
from app.schemas.category.read import CategoryRead
from app.schemas.region.read import RegionRead

router = APIRouter()


@router.get("/regions", status_code=status.HTTP_200_OK)
async def list_regions(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> list[RegionRead]:
    return await services.region.list_regions(db, cache)


@router.get("/categories", status_code=status.HTTP_200_OK)
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> list[CategoryRead]:
    return await services.category.list_categories(db, cache)
```

- [ ] **Step 6: Update service `__init__.py` exports if needed**

Check `app/services/category/__init__.py` and `app/services/region/__init__.py` — ensure `list_categories` / `list_regions` are re-exported. Update any callers that don't pass `cache`.

- [ ] **Step 7: Run test to verify it passes**

Run: `pytest tests/test_cache_static.py -v`
Expected: PASS

- [ ] **Step 8: Run full test suite**

Run: `mise run test`
Expected: PASS — all tests pass (existing callers updated)

- [ ] **Step 9: Run lint**

Run: `mise run lint`
Expected: PASS

- [ ] **Step 10: Commit**

```bash
git add app/services/category/read.py app/services/region/read.py app/routers/v1/utils.py tests/test_cache_static.py
git commit -m "feat: cache categories and regions at service layer"
```

---

### Task 6: Migrate pub/sub from Postgres to Redis

**Files:**
- Modify: `app/pubsub.py`
- Modify: `app/services/chat/message/create.py`
- Modify: `app/services/chat/message/update.py`
- Modify: `app/services/auth/validation.py`
- Create: `alembic/versions/xxxx_drop_notify_trigger.py` (via autogenerate)

- [ ] **Step 1: Create Alembic migration to drop the notify trigger**

Run: `alembic revision -m "drop notify_chat_members_new_message trigger"`

Then edit the generated file:

```python
"""drop notify_chat_members_new_message trigger

Revision ID: <auto-generated>
Revises: 5b5c5a10390e
Create Date: <auto-generated>
"""

from collections.abc import Sequence

from sqlalchemy import text

from alembic import op

revision: str = "<auto-generated>"
down_revision: str | None = "5b5c5a10390e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(text("DROP TRIGGER IF EXISTS new_chat_message ON chat_message"))
    op.execute(text("DROP FUNCTION IF EXISTS notify_chat_members_new_message"))


def downgrade() -> None:
    op.execute(
        text(
            "CREATE OR REPLACE FUNCTION notify_chat_members_new_message() "
            "RETURNS TRIGGER AS $$ "
            "DECLARE "
            "    borrower_id INTEGER; "
            "    owner_id INTEGER; "
            "    payload TEXT; "
            "BEGIN "
            "    borrower_id := new.borrower_id; "
            "    SELECT item.owner_id INTO owner_id FROM item "
            "        WHERE item.id = new.item_id; "
            "    payload := json_build_object("
            "        'type', 'new_chat_message', "
            "        'chat_message_id', new.id"
            "    )::text; "
            "    PERFORM pg_notify(format('user%s', borrower_id), payload); "
            "    PERFORM pg_notify(format('user%s', owner_id), payload); "
            "    RETURN NEW; "
            "END; "
            "$$ LANGUAGE plpgsql;"
        )
    )
    op.execute(
        text(
            "CREATE OR REPLACE TRIGGER new_chat_message "
            "AFTER INSERT ON chat_message "
            "FOR EACH ROW "
            "EXECUTE FUNCTION notify_chat_members_new_message();"
        )
    )
```

- [ ] **Step 2: Rewrite `app/pubsub.py` to use broadcaster (Redis)**

```python
from broadcaster import Broadcast

from app.schemas.pubsub import PubsubMessage


def get_broadcast() -> Broadcast:
    return _broadcast


_broadcast: Broadcast


def init_broadcast_dependency(broadcast: Broadcast) -> None:
    global _broadcast
    _broadcast = broadcast


async def notify_user(
    broadcast: Broadcast,
    user_id: int,
    message: PubsubMessage,
) -> None:
    channel = f"user{user_id}"
    await broadcast.publish(channel=channel, message=message.model_dump_json())
```

Key changes:
- Remove `notify_user` (sync, used `Session` + `pg_notify`) — it's not called anywhere except via the async variant
- Replace `notify_user_async` with `notify_user` that takes `Broadcast` instead of `AsyncSession`
- Uses `broadcast.publish()` instead of `pg_notify`

- [ ] **Step 3: Update `app/services/chat/message/create.py` — publish new message notifications**

After the `send_many_chat_messages` function returns the messages, add notification publishing. The function needs a `broadcast` parameter:

```python
from app.pubsub import get_broadcast, notify_user
from app.schemas.pubsub import PubsubMessageNewChatMessage


async def send_chat_message(
    db: AsyncSession,
    message: SendChatMessage,
    *,
    ensure_chat: bool = False,
) -> ChatMessageRead:
    chat_messages = await send_many_chat_messages(
        db=db,
        messages=[message],
        ensure_chats=ensure_chat,
    )
    return chat_messages[0]


async def send_many_chat_messages(
    db: AsyncSession,
    messages: list[SendChatMessage],
    *,
    ensure_chats: bool = False,
) -> list[ChatMessageRead]:
    # ... existing query/insert logic stays the same ...

    sent = [ChatMessageRead.model_validate(msg) for msg in sent_messages]

    # Publish notifications via Redis (replaces Postgres trigger)
    broadcast = get_broadcast()
    for chat_msg in sent:
        pubsub_msg = PubsubMessageNewChatMessage(chat_message_id=chat_msg.id)
        # Notify both chat members
        owner_id = (
            await db.execute(
                select(Item.owner_id).where(Item.id == chat_msg.item_id)
            )
        ).scalar_one()
        for user_id in {chat_msg.borrower_id, owner_id}:
            await notify_user(broadcast, user_id, pubsub_msg)

    return sent
```

Add `from sqlalchemy import select` and `from app.models.item import Item` to imports if not already present.

- [ ] **Step 4: Update `app/services/chat/message/update.py` — switch to Redis publish**

Change `mark_message_as_seen` to use `notify_user` with `broadcast` instead of `notify_user_async` with `db`:

```python
from app.pubsub import get_broadcast, notify_user

# In mark_message_as_seen, replace:
#     for user_id in {message.borrower_id, owner_id}:
#         await notify_user_async(db, user_id, pubsub_message)
# with:
    broadcast = get_broadcast()
    for user_id in {message.borrower_id, owner_id}:
        await notify_user(broadcast, user_id, pubsub_message)
```

Remove the `from app.pubsub import notify_user_async` import.

- [ ] **Step 5: Update `app/services/auth/validation.py` — switch to Redis publish**

In `validate_user_account`, replace:

```python
    await notify_user_async(
        db=db,
        user_id=user.id,
        message=PubsubMessageUpdatedAccountValidation(validated=True),
    )
```

with:

```python
    from app.pubsub import get_broadcast, notify_user

    await notify_user(
        broadcast=get_broadcast(),
        user_id=user.id,
        message=PubsubMessageUpdatedAccountValidation(validated=True),
    )
```

Remove the `from app.pubsub import notify_user_async` import.

- [ ] **Step 6: Run migrations**

Run: `alembic upgrade head`
Expected: migration applies, trigger is dropped

- [ ] **Step 7: Run full test suite**

Run: `mise run test`
Expected: PASS — all chat and websocket tests pass with Redis pub/sub

- [ ] **Step 8: Run lint**

Run: `mise run lint`
Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add alembic/versions/ app/pubsub.py app/services/chat/message/create.py app/services/chat/message/update.py app/services/auth/validation.py
git commit -m "feat: migrate pub/sub from Postgres LISTEN/NOTIFY to Redis"
```

---

### Task 7: Cache invalidation helpers

**Files:**
- Create: `app/services/item/cache.py`
- Create: `app/services/user/cache.py`
- Create: `app/services/chat/cache.py`
- Create: `app/services/loan/cache.py`

- [ ] **Step 1: Write test for item invalidation**

Create `tests/test_cache_invalidation.py`:

```python
import pytest
from redis.asyncio import Redis

from app.clients.cache import Cache
from app.services.item.cache import invalidate_item_created, invalidate_item_updated, invalidate_item_deleted


@pytest.fixture
async def redis_client():
    client = Redis(host="localhost", port=6379, db=3)
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.fixture
def cache(redis_client):
    return Cache(redis_client)


class TestItemInvalidation:
    async def test_invalidate_item_created(self, cache):
        await cache.set("babytroc:items:list:abc123", "data", ttl=60)
        await cache.set("babytroc:user:1:items:def456", "data", ttl=60)
        await cache.set("babytroc:user:1", '{"stars": 0}', ttl=60)

        await invalidate_item_created(cache, owner_id=1)

        assert await cache.get("babytroc:items:list:abc123") is None
        assert await cache.get("babytroc:user:1:items:def456") is None
        assert await cache.get("babytroc:user:1") is None

    async def test_invalidate_item_updated(self, cache):
        await cache.set("babytroc:item:42", "data", ttl=60)
        await cache.set("babytroc:items:list:abc123", "data", ttl=60)
        await cache.set("babytroc:user:1:items:def456", "data", ttl=60)

        await invalidate_item_updated(cache, item_id=42, owner_id=1)

        assert await cache.get("babytroc:item:42") is None
        assert await cache.get("babytroc:items:list:abc123") is None
        assert await cache.get("babytroc:user:1:items:def456") is None

    async def test_invalidate_item_deleted(self, cache):
        await cache.set("babytroc:item:42", "data", ttl=60)
        await cache.set("babytroc:items:list:abc123", "data", ttl=60)
        await cache.set("babytroc:user:1:items:def456", "data", ttl=60)
        await cache.set("babytroc:user:1:loans:ghi789", "data", ttl=60)
        await cache.set("babytroc:user:1:chats", "data", ttl=60)

        await invalidate_item_deleted(cache, item_id=42, owner_id=1)

        assert await cache.get("babytroc:item:42") is None
        assert await cache.get("babytroc:items:list:abc123") is None
        assert await cache.get("babytroc:user:1:items:def456") is None
        assert await cache.get("babytroc:user:1:loans:ghi789") is None
        assert await cache.get("babytroc:user:1:chats") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cache_invalidation.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Create `app/services/item/cache.py`**

```python
from app.cache_keys import (
    key_item,
    key_user,
    key_user_chats,
    pattern_items_list,
    pattern_user_items,
    pattern_user_loans,
)
from app.clients.cache import Cache


async def invalidate_item_created(cache: Cache, *, owner_id: int) -> None:
    await cache.delete_pattern(pattern_items_list())
    await cache.delete_pattern(pattern_user_items(owner_id))
    await cache.delete(key_user(owner_id))  # star count changes


async def invalidate_item_updated(cache: Cache, *, item_id: int, owner_id: int) -> None:
    await cache.delete(key_item(item_id))
    await cache.delete_pattern(pattern_items_list())
    await cache.delete_pattern(pattern_user_items(owner_id))


async def invalidate_item_deleted(cache: Cache, *, item_id: int, owner_id: int) -> None:
    await cache.delete(key_item(item_id))
    await cache.delete_pattern(pattern_items_list())
    await cache.delete_pattern(pattern_user_items(owner_id))
    await cache.delete_pattern(pattern_user_loans(owner_id))
    await cache.delete(key_user_chats(owner_id))


async def invalidate_item_liked(cache: Cache, *, liker_id: int, item_owner_id: int) -> None:
    from app.cache_keys import key_user_liked_items

    await cache.delete(key_user_liked_items(liker_id))
    await cache.delete(key_user(item_owner_id))  # like count


async def invalidate_item_saved(cache: Cache, *, saver_id: int) -> None:
    from app.cache_keys import key_user_saved_items

    await cache.delete(key_user_saved_items(saver_id))
```

- [ ] **Step 4: Create `app/services/user/cache.py`**

```python
from app.cache_keys import (
    key_user,
    pattern_items_list,
    pattern_user_all,
)
from app.clients.cache import Cache


async def invalidate_user_updated(cache: Cache, *, user_id: int) -> None:
    await cache.delete(key_user(user_id))


async def invalidate_user_validated(cache: Cache, *, user_id: int) -> None:
    await cache.delete(key_user(user_id))
    await cache.delete_pattern(pattern_items_list())  # visibility may change


async def invalidate_user_deleted(cache: Cache, *, user_id: int) -> None:
    await cache.delete_pattern(pattern_user_all(user_id))
    await cache.delete(key_user(user_id))
    await cache.delete_pattern(pattern_items_list())
```

- [ ] **Step 5: Create `app/services/chat/cache.py`**

```python
from app.cache_keys import key_user_chats, pattern_chat_messages
from app.clients.cache import Cache


async def invalidate_chat_message_sent(
    cache: Cache,
    *,
    item_id: int,
    borrower_id: int,
    owner_id: int,
) -> None:
    await cache.delete(key_user_chats(owner_id))
    await cache.delete(key_user_chats(borrower_id))
    await cache.delete_pattern(pattern_chat_messages(item_id, borrower_id))


async def invalidate_chat_message_seen(
    cache: Cache,
    *,
    item_id: int,
    borrower_id: int,
) -> None:
    await cache.delete_pattern(pattern_chat_messages(item_id, borrower_id))
```

- [ ] **Step 6: Create `app/services/loan/cache.py`**

```python
from app.cache_keys import (
    key_item,
    pattern_chat_messages,
    pattern_items_list,
    pattern_user_borrowings,
    pattern_user_loans,
)
from app.clients.cache import Cache


async def invalidate_loan_request_created(
    cache: Cache,
    *,
    item_id: int,
    borrower_id: int,
    owner_id: int,
) -> None:
    await cache.delete(key_item(item_id))
    await cache.delete_pattern(pattern_user_borrowings(borrower_id))
    await cache.delete_pattern(pattern_user_loans(owner_id))
    from app.cache_keys import key_user_chats

    await cache.delete(key_user_chats(owner_id))
    await cache.delete(key_user_chats(borrower_id))
    await cache.delete_pattern(pattern_chat_messages(item_id, borrower_id))


async def invalidate_loan_request_state_changed(
    cache: Cache,
    *,
    item_id: int,
    borrower_id: int,
    owner_id: int,
) -> None:
    await cache.delete(key_item(item_id))
    await cache.delete_pattern(pattern_user_borrowings(borrower_id))
    await cache.delete_pattern(pattern_user_loans(owner_id))
    await cache.delete_pattern(pattern_chat_messages(item_id, borrower_id))


async def invalidate_loan_started(
    cache: Cache,
    *,
    item_id: int,
    borrower_id: int,
    owner_id: int,
) -> None:
    await cache.delete(key_item(item_id))
    await cache.delete_pattern(pattern_items_list())  # availability changes
    await cache.delete_pattern(pattern_user_borrowings(borrower_id))
    await cache.delete_pattern(pattern_user_loans(owner_id))
    await cache.delete_pattern(pattern_chat_messages(item_id, borrower_id))


async def invalidate_loan_ended(
    cache: Cache,
    *,
    item_id: int,
    borrower_id: int,
    owner_id: int,
) -> None:
    await cache.delete(key_item(item_id))
    await cache.delete_pattern(pattern_items_list())  # availability changes
    await cache.delete_pattern(pattern_user_borrowings(borrower_id))
    await cache.delete_pattern(pattern_user_loans(owner_id))
    await cache.delete_pattern(pattern_chat_messages(item_id, borrower_id))
```

- [ ] **Step 7: Run test to verify it passes**

Run: `pytest tests/test_cache_invalidation.py -v`
Expected: PASS

- [ ] **Step 8: Run lint**

Run: `mise run lint`
Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add app/services/item/cache.py app/services/user/cache.py app/services/chat/cache.py app/services/loan/cache.py tests/test_cache_invalidation.py
git commit -m "feat: add cache invalidation helpers for all domains"
```

---

### Task 8: Wire invalidation into write services

**Files:**
- Modify: `app/services/item/create.py`
- Modify: `app/services/item/update.py`
- Modify: `app/services/item/delete.py`
- Modify: `app/services/item/like/create.py`
- Modify: `app/services/item/like/delete.py`
- Modify: `app/services/item/save/create.py`
- Modify: `app/services/item/save/delete.py`
- Modify: `app/services/chat/message/create.py`
- Modify: `app/services/chat/message/update.py`
- Modify: `app/services/user/update.py`
- Modify: `app/services/user/delete.py`
- Modify: `app/services/auth/validation.py`
- Modify: `app/services/loan/request/create.py`
- Modify: `app/services/loan/request/accept.py` (or equivalent)
- Modify: `app/services/loan/request/reject.py`
- Modify: `app/services/loan/request/cancel.py`
- Modify: `app/services/loan/loan/create.py`
- Modify: `app/services/loan/loan/update.py`
- Modify: all routers that call these services (to pass `cache`)

This task is the largest — it touches every write service to add cache invalidation after the DB write. The pattern is the same everywhere:

1. Add `cache: Cache` parameter to the write function
2. Call the appropriate `invalidate_*` helper after the DB operation
3. Update the router to inject `cache` via `Depends(get_cache)` and pass it to the service

- [ ] **Step 1: Update item write services**

For each of `create.py`, `update.py`, `delete.py`:

Add `cache: Cache` parameter. After the DB write, call the invalidation helper.

Example for `create_item`:
```python
from app.clients.cache import Cache
from app.services.item.cache import invalidate_item_created

async def create_item(
    db: AsyncSession,
    owner_id: int,
    item_create: ItemCreate,
    cache: Cache,
) -> ItemRead:
    # ... existing logic ...
    result = ...
    await invalidate_item_created(cache, owner_id=owner_id)
    return result
```

Example for `update_item`:
```python
from app.services.item.cache import invalidate_item_updated

async def update_item(
    db: AsyncSession,
    *,
    item_id: int,
    item_update: ItemUpdate,
    query_filter: ItemUpdateQueryFilter | None = None,
    cache: Cache,
) -> ItemRead:
    # ... existing logic ...
    result = ...
    await invalidate_item_updated(cache, item_id=item_id, owner_id=result.owner.id)
    return result
```

Example for `delete_item`:
```python
from app.services.item.cache import invalidate_item_deleted

async def delete_item(
    db: AsyncSession,
    item_id: int,
    *,
    query_filter: ItemDeleteQueryFilter | None = None,
    cache: Cache,
) -> None:
    # Get owner_id before deleting
    owner_id = (await db.execute(select(Item.owner_id).where(Item.id == item_id))).scalar_one()
    # ... existing delete logic ...
    await invalidate_item_deleted(cache, item_id=item_id, owner_id=owner_id)
```

- [ ] **Step 2: Update like/save services**

For `like/create.py` and `like/delete.py`:
```python
async def add_item_to_user_liked_items(db, *, item_id, user_id, cache):
    # ... existing logic ...
    # Get item owner for like count invalidation
    owner_id = (await db.execute(select(Item.owner_id).where(Item.id == item_id))).scalar_one()
    await invalidate_item_liked(cache, liker_id=user_id, item_owner_id=owner_id)
```

For `save/create.py` and `save/delete.py`:
```python
async def add_item_to_user_saved_items(db, *, item_id, user_id, cache):
    # ... existing logic ...
    await invalidate_item_saved(cache, saver_id=user_id)
```

- [ ] **Step 3: Update chat message create with invalidation**

In `app/services/chat/message/create.py`, after the notification publish (added in Task 6), add:

```python
from app.cache import get_cache
from app.services.chat.cache import invalidate_chat_message_sent

async def send_many_chat_messages(...) -> list[ChatMessageRead]:
    # ... existing logic + notification from Task 6 ...

    cache = get_cache()
    for chat_msg in sent:
        owner_id = ...  # already fetched for notifications
        await invalidate_chat_message_sent(
            cache,
            item_id=chat_msg.item_id,
            borrower_id=chat_msg.borrower_id,
            owner_id=owner_id,
        )

    return sent
```

- [ ] **Step 4: Update chat message update with invalidation**

In `mark_message_as_seen`:
```python
from app.cache import get_cache
from app.services.chat.cache import invalidate_chat_message_seen

async def mark_message_as_seen(...) -> ChatMessageRead:
    # ... existing logic ...
    cache = get_cache()
    await invalidate_chat_message_seen(
        cache,
        item_id=message.item_id,
        borrower_id=message.borrower_id,
    )
    return ChatMessageRead.model_validate(message)
```

- [ ] **Step 5: Update user write services**

In `app/services/user/update.py`:
```python
async def update_user(db, user_id, user_update, cache):
    # ... existing logic ...
    await invalidate_user_updated(cache, user_id=user_id)
    return result
```

In `app/services/user/delete.py`:
```python
async def delete_user(db, user_id, cache):
    # ... existing logic ...
    await invalidate_user_deleted(cache, user_id=user_id)
```

In `app/services/auth/validation.py` (`validate_user_account`):
```python
    await invalidate_user_validated(cache, user_id=user.id)
```

- [ ] **Step 6: Update loan services**

For each loan request state change (accept, reject, cancel) and loan lifecycle (execute/create, end):

```python
# In loan request create:
await invalidate_loan_request_created(cache, item_id=..., borrower_id=..., owner_id=...)

# In loan request accept/reject/cancel:
await invalidate_loan_request_state_changed(cache, item_id=..., borrower_id=..., owner_id=...)

# In loan execute (start):
await invalidate_loan_started(cache, item_id=..., borrower_id=..., owner_id=...)

# In loan end:
await invalidate_loan_ended(cache, item_id=..., borrower_id=..., owner_id=...)
```

- [ ] **Step 7: Update all routers to pass `cache` to write services**

Every router calling a write service needs:
```python
from app.cache import get_cache
from app.clients.cache import Cache

# Add to endpoint signature:
cache: Annotated[Cache, Depends(get_cache)],

# Pass to service call:
await services.item.create_item(db, owner_id, item_create, cache)
```

This affects routers in: `me/items/create.py`, `me/items/update.py`, `me/items/delete.py`, `me/liked.py`, `me/saved.py`, `me/chats/create.py`, `me/chats/update.py`, `me/me.py`, `items/request.py`, `me/loans/requests/update.py`, `me/borrowings/requests/update.py`, `me/items/loans/update.py`, `auth/validate.py` (if it has a router).

- [ ] **Step 8: Run full test suite**

Run: `mise run test`
Expected: PASS — all tests pass with invalidation wired in

- [ ] **Step 9: Run lint**

Run: `mise run lint`
Expected: PASS

- [ ] **Step 10: Commit**

```bash
git add app/services/ app/routers/
git commit -m "feat: wire cache invalidation into all write services and routers"
```

---

### Task 9: Add caching to read services (items, users)

**Files:**
- Modify: `app/services/item/read/get.py`
- Modify: `app/services/user/read.py`
- Modify: routers calling these services

This task adds cache-aside reads for the highest-value single-entity lookups. List/search endpoint caching is deferred to Task 10.

- [ ] **Step 1: Write test for cached item detail**

Add to `tests/test_cache_static.py` (or create `tests/test_cache_reads.py`):

```python
class TestCachedItemDetail:
    async def test_item_detail_cached(self, alice_client, app, alice_item):
        cache: Cache = app.state.cache
        item_id = alice_item["id"]

        # First call — cache miss
        r1 = await alice_client.get(f"/api/v1/items/{item_id}")
        assert r1.status_code == 200

        # Verify cached (core data without per-user flags)
        cached = await cache.get(f"babytroc:item:{item_id}")
        assert cached is not None

        # Second call — hits cache
        r2 = await alice_client.get(f"/api/v1/items/{item_id}")
        assert r2.status_code == 200


class TestCachedUserProfile:
    async def test_user_profile_cached(self, alice_client, app, alice):
        cache: Cache = app.state.cache
        user_id = alice.id

        r1 = await alice_client.get(f"/api/v1/users/{user_id}")
        assert r1.status_code == 200

        cached = await cache.get(f"babytroc:user:{user_id}")
        assert cached is not None
```

- [ ] **Step 2: Add caching to `app/services/item/read/get.py`**

The tricky part: `get_item` currently returns `ItemRead` with per-user flags (`owned`, `liked`, `saved`). The cache stores core item data WITHOUT these flags. On cache hit, flags must be resolved separately.

Read the existing `get_item` code carefully. Split into:
1. Core item fetch (cacheable) — no `client_id` dependent columns
2. Per-user flag resolution (from cached liked/saved sets)

```python
from app.cache_keys import TTL_ITEM, key_item
from app.clients.cache import Cache

async def get_item(
    db: AsyncSession,
    item_id: int,
    *,
    query_filter: ItemReadQueryFilter | None = None,
    client_id: int | None = None,
    cache: Cache,
) -> ItemRead:
    # Try cache for core data
    cached = await cache.get(key_item(item_id))
    if cached is not None:
        item = ItemRead.model_validate_json(cached)
    else:
        # Existing DB query (without client_id-dependent columns)
        item = await _query_item(db, item_id, query_filter=query_filter)
        await cache.set(key_item(item_id), item.model_dump_json(), ttl=TTL_ITEM)

    # Resolve per-user flags
    if client_id is not None:
        item = await _resolve_per_user_flags(db, cache, item, client_id)

    return item
```

This requires refactoring the existing query to separate core data from per-user flags. The exact implementation depends on the current query structure — read the file first and adapt.

- [ ] **Step 3: Add per-user flag resolution helper**

Create a helper in `app/services/item/read/get.py` or a shared location:

```python
from app.cache_keys import TTL_USER_LIKED, TTL_USER_SAVED, key_user_liked_items, key_user_saved_items

async def _get_user_liked_item_ids(db: AsyncSession, cache: Cache, user_id: int) -> set[int]:
    cached = await cache.get(key_user_liked_items(user_id))
    if cached is not None:
        return set(json.loads(cached))

    stmt = select(ItemLike.item_id).where(ItemLike.user_id == user_id)
    result = (await db.execute(stmt)).scalars().all()
    ids = list(result)
    await cache.set(key_user_liked_items(user_id), json.dumps(ids), ttl=TTL_USER_LIKED)
    return set(ids)


async def _get_user_saved_item_ids(db: AsyncSession, cache: Cache, user_id: int) -> set[int]:
    cached = await cache.get(key_user_saved_items(user_id))
    if cached is not None:
        return set(json.loads(cached))

    stmt = select(ItemSave.item_id).where(ItemSave.user_id == user_id)
    result = (await db.execute(stmt)).scalars().all()
    ids = list(result)
    await cache.set(key_user_saved_items(user_id), json.dumps(ids), ttl=TTL_USER_SAVED)
    return set(ids)


async def _resolve_per_user_flags(
    db: AsyncSession,
    cache: Cache,
    item: ItemRead,
    client_id: int,
) -> ItemRead:
    liked_ids = await _get_user_liked_item_ids(db, cache, client_id)
    saved_ids = await _get_user_saved_item_ids(db, cache, client_id)

    return item.model_copy(update={
        "liked": item.id in liked_ids,
        "saved": item.id in saved_ids,
        "owned": item.owner.id == client_id,
    })
```

Note: Check if `ItemRead` uses aliases (`liked_by_client`, etc.) and use the correct field names.

- [ ] **Step 4: Add caching to `app/services/user/read.py`**

For `get_user`:
```python
from app.cache_keys import TTL_USER, key_user
from app.clients.cache import Cache

async def get_user(db: AsyncSession, user_id: int, cache: Cache) -> UserRead:
    cached = await cache.get(key_user(user_id))
    if cached is not None:
        return UserRead.model_validate_json(cached)

    # existing query...
    user = await _query_user(db, user_id)
    schema = UserRead.model_validate(user)
    await cache.set(key_user(user_id), schema.model_dump_json(), ttl=TTL_USER)
    return schema
```

- [ ] **Step 5: Update routers to pass `cache` to read services**

Update `app/routers/v1/items/read.py`, `app/routers/v1/users/read.py`, etc. to inject `cache` and pass to service calls.

- [ ] **Step 6: Run full test suite**

Run: `mise run test`
Expected: PASS

- [ ] **Step 7: Run lint**

Run: `mise run lint`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add app/services/item/read/ app/services/user/read.py app/routers/
git commit -m "feat: add cache-aside reads for item detail and user profile"
```

---

### Task 10: Cache list/search endpoints

**Files:**
- Modify: `app/services/item/read/list.py`
- Modify: `app/services/chat/chat/read.py`
- Modify: `app/services/chat/message/read.py`
- Modify: routers calling these services

This task caches the remaining read-heavy endpoints: item search/list, chat lists, and chat messages.

- [ ] **Step 1: Add caching to item list/search**

In `app/services/item/read/list.py`, wrap the query with cache-aside using `cache_key_hash` from the query filter parameters:

```python
from app.cache_keys import TTL_ITEMS_LIST, cache_key_hash
from app.clients.cache import Cache

async def list_items(
    db: AsyncSession,
    words: list[str] | None = None,
    *,
    query_filter: ItemReadQueryFilter | None = None,
    page_options: ...,
    client_id: int | None = None,
    cache: Cache,
) -> QueryPageResult[...]:
    # Build cache key from all query parameters
    key = f"babytroc:items:list:{cache_key_hash(
        words=tuple(words) if words else None,
        query_filter=str(query_filter) if query_filter else None,
        page_options=str(page_options) if page_options else None,
    )}"

    # Cache stores core results only (no per-user flags)
    # ... cache-aside pattern ...
    # After fetching results, resolve per-user flags using _resolve_per_user_flags
```

Note: The exact implementation depends on the overloaded signatures and pagination cursor types. Read the file carefully and adapt.

- [ ] **Step 2: Add caching to chat list and messages**

Same pattern for `list_chats` and `list_messages`. These are always per-user (filtered by `member_id`), so the cache key includes the user ID implicitly via the query filter.

- [ ] **Step 3: Update all routers calling these services**

Add `cache` parameter injection to list endpoints.

- [ ] **Step 4: Run full test suite**

Run: `mise run test`
Expected: PASS

- [ ] **Step 5: Run lint**

Run: `mise run lint`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add app/services/ app/routers/
git commit -m "feat: add caching to item search, chat lists, and chat messages"
```

---

### Task 11: Update Docker Compose

**Files:**
- Modify: `../compose.yaml` (project root)

- [ ] **Step 1: Read current compose.yaml**

Read `../compose.yaml` to understand current structure.

- [ ] **Step 2: Add Redis service**

Add to the services section:

```yaml
  redis:
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    restart: unless-stopped
```

- [ ] **Step 3: Add volume**

Add to the volumes section (create if it doesn't exist):

```yaml
volumes:
  redis-data:
```

- [ ] **Step 4: Update API service dependencies**

Add `redis` to the API service's `depends_on`:

```yaml
  babytroc-api:
    depends_on:
      - images
      - redis
```

- [ ] **Step 5: Add Redis env vars to compose env**

If the compose file references an `.env` file, add:

```
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=2
```

- [ ] **Step 6: Commit**

```bash
git add ../compose.yaml
git commit -m "feat: add Redis service to Docker Compose"
```

---

### Task 12: Final integration test and cleanup

**Files:**
- Modify: tests as needed

- [ ] **Step 1: Write end-to-end cache integration test**

Create `tests/test_cache_integration.py`:

```python
class TestCacheIntegration:
    async def test_item_create_invalidates_list_cache(
        self, alice_client, app, alice_item_data
    ):
        """Creating an item invalidates the items list cache."""
        cache = app.state.cache

        # Populate list cache
        r1 = await alice_client.get("/api/v1/items")
        assert r1.status_code == 200
        initial_count = len(r1.json())

        # Create item
        r2 = await alice_client.post("/api/v1/me/items", json=alice_item_data)
        assert r2.status_code in (200, 201)

        # List should reflect new item (cache invalidated)
        r3 = await alice_client.get("/api/v1/items")
        assert r3.status_code == 200
        assert len(r3.json()) == initial_count + 1

    async def test_like_updates_per_user_flags(
        self, alice_client, bob_client, app, bob_item
    ):
        """Liking an item updates the per-user liked flag."""
        item_id = bob_item["id"]

        # Like the item
        await alice_client.post(f"/api/v1/me/liked/{item_id}")

        # Verify flag
        r = await alice_client.get(f"/api/v1/items/{item_id}")
        assert r.status_code == 200
        assert r.json()["liked_by_client"] is True
```

Adapt the test to use the actual fixture names and API paths from the project.

- [ ] **Step 2: Run full test suite**

Run: `mise run test`
Expected: PASS — all tests pass

- [ ] **Step 3: Run lint**

Run: `mise run lint`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test: add end-to-end cache integration tests"
```
