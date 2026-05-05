# Redis Caching & Pub/Sub Migration

**Date:** 2026-05-04
**Goal:** Add Redis-based caching at the service layer to prepare for scale, and migrate real-time pub/sub from Postgres LISTEN/NOTIFY to Redis.

## 1. Redis Service

Redis runs as a standalone process on the host (Gentoo: `emerge -av dev-db/redis`, managed via OpenRC).

Configuration (`/etc/redis/redis.conf`):

```conf
bind 127.0.0.1
port 6379
maxmemory 256mb
maxmemory-policy allkeys-lru
appendonly yes
```

Use a dedicated database number (e.g. `db=2`) to avoid collisions with other services. Tests use a separate database number (e.g. `db=3`), flushed between runs.

## 2. Dependencies

- Add `redis[hiredis]` to `pyproject.toml`
- Replace `broadcaster[postgres]` with `broadcaster[redis]`

## 3. Configuration

New `RedisConfig` NamedTuple in `app/config.py`, following the existing pattern:

```python
class RedisConfig(NamedTuple):
    host: str
    port: int
    db: int
    password: str | None

    @classmethod
    def from_env(cls, **kwargs):
        return cls(
            host=kwargs.get("host", os.environ.get("REDIS_HOST", "localhost")),
            port=int(kwargs.get("port", os.environ.get("REDIS_PORT", "6379"))),
            db=int(kwargs.get("db", os.environ.get("REDIS_DB", "0"))),
            password=kwargs.get("password", os.environ.get("REDIS_PASSWORD")),
        )
```

Add `redis: RedisConfig` field to `Config`. Update `PubsubConfig` to build a Redis DSN instead of a Postgres DSN.

Env vars: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD` (optional).

## 4. App Integration

### Client (`app/clients/redis.py`)

Thin wrapper: creates `redis.asyncio.Redis` from `RedisConfig`. Initialized in `create_app()`, stored on `app.state.redis`, closed in the lifespan shutdown handler.

### Cache abstraction (`app/clients/cache.py`)

```python
class Cache:
    def __init__(self, redis: Redis): ...

    async def get(self, key: str) -> bytes | None
    async def set(self, key: str, value: str, ttl: int)
    async def delete(self, *keys: str)
    async def delete_pattern(self, pattern: str)  # SCAN + DELETE (not KEYS)
    async def get_or_set(self, key: str, ttl: int, factory: Callable) -> str
```

Stored on `app.state.cache`. Exposed via `get_cache()` FastAPI dependency.

### Serialization

Pydantic's built-in JSON serialization (`.model_dump_json()` / `model_validate_json()`). No additional serialization library needed. Cache stores JSON strings.

## 5. Cache Key Strategy

### Naming convention

`babytroc:{domain}:{identifier}:{variant}`

### Key catalog

| Key | Content | TTL |
|---|---|---|
| `babytroc:categories` | All categories | 24h |
| `babytroc:regions` | All regions | 24h |
| `babytroc:item:{id}` | Single item core data (no per-user flags) | 10min |
| `babytroc:items:list:{query_hash}` | Item search results (IDs + core data) | 2min |
| `babytroc:user:{id}` | User profile | 30min |
| `babytroc:user:{id}:liked_items` | List of item IDs the user has liked | 5min |
| `babytroc:user:{id}:saved_items` | List of item IDs the user has saved | 5min |
| `babytroc:user:{id}:items:{query_hash}` | User's own items list | 5min |
| `babytroc:user:{id}:chats` | User's chat list | 2min |
| `babytroc:chat:{id}:messages:{page_hash}` | Paginated messages in a chat | 2min |
| `babytroc:user:{id}:loans:{query_hash}` | User's loans | 5min |
| `babytroc:user:{id}:borrowings:{query_hash}` | User's borrowings | 5min |

### Query hash generation

Deterministic hash from sorted, non-None query parameters:

```python
def cache_key_hash(**params) -> str:
    filtered = {k: v for k, v in sorted(params.items()) if v is not None}
    raw = json.dumps(filtered, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
```

## 6. Per-User Data Splitting

Item data is cached globally (core data without per-user flags). Per-user flags are resolved cheaply at read time:

1. **`liked_by_client`** — check `item.id in cached_liked_item_ids` (set lookup)
2. **`saved_by_client`** — check `item.id in cached_saved_item_ids` (set lookup)
3. **`owned_by_client`** — `item.owner_id == client_id` (no cache needed)

The `liked_items` and `saved_items` sets are fetched via lightweight queries (`SELECT item_id FROM item_like WHERE user_id = :id`) and cached per-user.

## 7. Cache Invalidation

Explicit invalidation on every write. TTL is a safety net only.

### Invalidation map

| Write operation | Keys invalidated |
|---|---|
| **Item create** | `items:list:*`, `user:{owner}:items:*`, `user:{owner}` (star count) |
| **Item update** | `item:{id}`, `items:list:*`, `user:{owner}:items:*` |
| **Item delete** | `item:{id}`, `items:list:*`, `user:{owner}:items:*`, `user:{owner}:loans:*`, `user:{owner}:chats` |
| **Like item** | `user:{liker}:liked_items`, `user:{item_owner}` (like count) |
| **Unlike item** | `user:{liker}:liked_items`, `user:{item_owner}` (like count) |
| **Save item** | `user:{saver}:saved_items` |
| **Unsave item** | `user:{saver}:saved_items` |
| **Loan request create** | `item:{id}`, `user:{borrower}:borrowings:*`, `user:{owner}:loans:*`, `user:{owner}:chats`, `user:{borrower}:chats`, `chat:{id}:messages:*` |
| **Loan request accept** | `item:{id}`, `user:{borrower}:borrowings:*`, `user:{owner}:loans:*`, `chat:{id}:messages:*` |
| **Loan request reject** | `item:{id}`, `user:{borrower}:borrowings:*`, `user:{owner}:loans:*`, `chat:{id}:messages:*` |
| **Loan request cancel** | `item:{id}`, `user:{borrower}:borrowings:*`, `user:{owner}:loans:*`, `chat:{id}:messages:*` |
| **Loan execute (start)** | `item:{id}`, `items:list:*`, `user:{borrower}:borrowings:*`, `user:{owner}:loans:*`, `chat:{id}:messages:*` |
| **Loan end (return)** | `item:{id}`, `items:list:*`, `user:{borrower}:borrowings:*`, `user:{owner}:loans:*`, `chat:{id}:messages:*` |
| **Chat message send** | `user:{owner}:chats`, `user:{borrower}:chats`, `chat:{id}:messages:*` |
| **Message mark seen** | `chat:{id}:messages:*` |
| **User update** | `user:{id}` |
| **User validation** | `user:{id}`, `items:list:*` (visibility may change) |
| **User delete** | `user:{id}`, `user:{id}:*`, `items:list:*`, related `chat:*`, `item:{owned_ids}` |
| **Category create** | `categories` |
| **Region create** | `regions` |

### Item delete and liked/saved sets

When an item is deleted, we do NOT attempt to find all users who liked/saved it. The 5min TTL on `user:{id}:liked_items` and `user:{id}:saved_items` handles staleness naturally. Read endpoints filter out deleted items gracefully.

### Invalidation helpers

Each domain gets a `services/{domain}/cache.py` with invalidation functions:

```python
async def invalidate_item(cache: Cache, item_id: int, owner_id: int):
    await cache.delete(f"babytroc:item:{item_id}")
    await cache.delete_pattern("babytroc:items:list:*")
    await cache.delete_pattern(f"babytroc:user:{owner_id}:items:*")
```

These are called from write services after the DB commit.

## 8. Pub/Sub Migration

### Current state

- `broadcaster[postgres]` backed by Postgres `LISTEN/NOTIFY`
- Postgres trigger `notify_chat_members_new_message` fires `pg_notify()` on `chat_message` INSERT
- WebSocket handler subscribes to `user{id}` channels via broadcaster

### Target state

- `broadcaster[redis]` backed by Redis pub/sub
- Postgres trigger removed (new Alembic migration: `DROP TRIGGER` + `DROP FUNCTION`)
- `send_chat_message()` service publishes to Redis directly after DB insert
- Same channel naming: `user{id}`, same payload shape: `{type, chat_message_id}`
- WebSocket handler unchanged — still subscribes via broadcaster

### Migration steps

1. Add Alembic migration to drop `notify_chat_members_new_message` trigger and function
2. Update `PubsubConfig` to produce a Redis DSN
3. Update all services that publish notifications to use Redis pub/sub instead of `pg_notify`:
   - `send_chat_message()` — currently implicit via Postgres trigger; add explicit Redis publish after DB insert
   - `mark_message_as_seen()` — currently calls `notify_user_async()` which uses `pg_notify`; switch to Redis publish
   - `update_user_validation()` — currently calls `notify_user_async()` which uses `pg_notify`; switch to Redis publish
4. Replace `notify_user_async()` in `app/pubsub.py` (which wraps `pg_notify`) with a Redis-based equivalent
5. Verify WebSocket handler works without changes

## 9. Service Layer Changes

### Read services

Cache-aside pattern: check cache first, query DB on miss, populate cache after. Cached reads return Pydantic schemas (not ORM objects), since that's what gets serialized. Routers already consume schemas, so this is a natural fit.

```python
async def get_item(db: AsyncSession, cache: Cache, item_id: int) -> ItemSchema:
    cached = await cache.get(f"babytroc:item:{item_id}")
    if cached:
        return ItemSchema.model_validate_json(cached)

    item = await _query_item(db, item_id)
    schema = ItemSchema.model_validate(item)
    await cache.set(
        f"babytroc:item:{item_id}",
        schema.model_dump_json(),
        ttl=600,
    )
    return schema
```

### Write services

Perform DB write, then invalidate. The `Cache` parameter is added alongside `AsyncSession`.

```python
async def update_item(db: AsyncSession, cache: Cache, item_id: int, ...):
    item = await _do_update(db, item_id, ...)
    await invalidate_item(cache, item_id, item.owner_id)
    return item
```

## 10. Testing

- Real Redis required in test environment (same Gentoo host or CI)
- Tests use a dedicated Redis DB number (e.g. `3`), configured via `REDIS_DB` env var
- Test fixtures flush the Redis test DB between test sessions
- No in-memory fake — tests verify real serialization and invalidation behavior
- Existing test patterns (alice/bob/carol clients, httpx.AsyncClient) remain unchanged

## 11. What Does NOT Change

- **Routers** — no changes, they call services
- **Pydantic schemas** — used as-is for cache serialization
- **WebSocket handler** — still subscribes via broadcaster, just Redis-backed now
- **Test fixtures** — same user/client patterns, just need Redis available
- **Alembic** — only one new migration (drop trigger)

## 12. Docker Compose (Production)

For Docker-based deployments, add to `compose.yaml`:

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

Add `depends_on: [images, redis]` to the API service. Add `redis-data` to the volumes section.
