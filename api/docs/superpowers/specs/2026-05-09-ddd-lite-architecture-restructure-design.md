# DDD-Lite Architecture Restructure

**Date:** 2026-05-09
**Status:** Draft
**Branch:** Separate branch (from main)

## Problem Statement

The current layered architecture (`models/`, `schemas/`, `services/`, `routers/`, `errors/`) causes:

1. **Schema duplication** -- the same fields defined across base, create, update, read, and preview schemas per domain.
2. **Monolithic query logic** -- services like `item/read/list.py` (350+ LOC) build complex SQL with conditional subqueries, overloaded type hints, and scattered filter logic. Hard to verify, hard to compose, hard to test in isolation.
3. **Implicit query construction** -- schema query params are translated into SQLAlchemy filters in non-obvious ways. Adding a new filter means modifying a large function rather than composing a small, testable piece.
4. **CRUD ceremony** -- every new operation requires touching create/read/update/delete files plus `__init__.py` re-exports, even for trivial operations.
5. **Split persistence** -- some DB operations live in `clients/database/`, others in `services/`. No clear rule for where persistence logic belongs.

## Goals

- Code organized by domain (bounded context), not technical layer
- Composable, testable query filter functions (pure `Select -> Select`)
- Fewer schemas per domain with less field duplication
- Explicit cross-domain dependencies with clear import rules
- Single transaction for all operations (no event bus complexity)
- Full restructure on a dedicated branch

## Non-Goals

- Repository abstraction layer (services keep direct `AsyncSession` access)
- Domain events / event bus
- Aggregate root enforcement
- Unit of Work pattern
- CQRS or event sourcing

## Architecture Overview

### Directory Structure

```
app/
  domains/
    item/
      __init__.py          # public API exports
      models.py            # Item, ItemImage, ItemCategory, ItemRegion, ItemLike, ItemSave
      schemas.py           # ItemCreate, ItemUpdate, ItemRead, ItemPreview
      filters.py           # composable Select -> Select functions
      services.py          # business logic (or services/ if large)
      errors.py            # ItemNotFoundError, etc.
      enums.py             # ItemQueryAvailability (if domain-specific)
    chat/
      __init__.py
      models.py            # Chat, ChatMessage
      schemas.py
      filters.py
      services.py
      errors.py
    loan/
      __init__.py
      models.py            # Loan, LoanRequest
      schemas.py
      filters.py
      services.py
      errors.py
    user/
      __init__.py
      models.py            # User
      schemas.py
      filters.py
      services.py
      errors.py
    auth/
      __init__.py
      models.py            # RefreshToken, PasswordResetToken
      schemas.py
      filters.py
      services.py
      errors.py
    image/
      __init__.py
      models.py
      schemas.py
      services.py
      errors.py
    region/
      __init__.py
      models.py
      schemas.py
      services.py
    category/
      __init__.py
      models.py
      schemas.py
      services.py
    report/
      __init__.py
      models.py
      schemas.py
      services.py
  routers/
    __init__.py
    v1/
      __init__.py
      auth/
        __init__.py
        router.py
        annotations.py
      items/
        __init__.py
        router.py
        annotations.py
        queries.py          # query param schemas (router concern)
      me/
        __init__.py
        router.py
        annotations.py
        chats/
          __init__.py
          router.py
          annotations.py
          websocket.py
          queries.py
        items/
          __init__.py
          router.py
          annotations.py
          queries.py
          loans/
            __init__.py
            router.py
            annotations.py
            requests/
              __init__.py
              router.py
              annotations.py
        borrowings/
          __init__.py
          router.py
          annotations.py
          requests/
            __init__.py
            router.py
            annotations.py
        loans/
          __init__.py
          router.py
          annotations.py
          requests/
            __init__.py
            router.py
            annotations.py
      users/
        __init__.py
        router.py
        annotations.py
      images/
        __init__.py
        router.py
  infrastructure/
    database.py            # engine, session maker, get_db_session
    cache.py               # Cache client + get_cache dependency
    cache_keys.py          # cache key builders
    pubsub.py              # Broadcast + get_broadcast + notify helpers
    email.py               # FastMail + get_email_client dependency
    redis.py               # Redis client factory
    storage.py             # S3/MinIO client
    config.py              # Config, DatabaseConfig, etc.
  shared/
    pagination.py          # QueryPageCursor, QueryPageOptions, QueryPageResult
    schemas.py             # shared base schemas
    filters.py             # generic filter helpers (paginate, order_by_newest, with_count)
    utils.py               # integer_range_to_inclusive, other shared helpers
  app.py                   # create_app, exception handlers, middlewares
  main.py                  # entry point
  __init__.py
```

### What Gets Deleted

| Old location | New location |
|---|---|
| `app/models/` | `app/domains/*/models.py` |
| `app/schemas/` | `app/domains/*/schemas.py` + `app/routers/v1/*/queries.py` + `app/shared/` |
| `app/services/` | `app/domains/*/services.py` |
| `app/errors/` | `app/domains/*/errors.py` |
| `app/clients/database/` | Absorbed into `app/domains/*/services.py` |
| `app/clients/email/` | `app/infrastructure/email.py` (client) + `app/domains/auth/services.py` (send logic) |
| `app/clients/networking/` | `app/infrastructure/` or relevant domain |
| `app/clients/storage/` | `app/infrastructure/storage.py` |
| `app/clients/cache.py` | `app/infrastructure/cache.py` |
| `app/clients/redis.py` | `app/infrastructure/redis.py` |
| `app/domain/star.py` | `app/domains/user/services.py` (star reward calculation) |
| `app/config.py` | `app/infrastructure/config.py` |
| `app/database.py` | `app/infrastructure/database.py` |
| `app/pubsub.py` | `app/infrastructure/pubsub.py` |
| `app/email.py` | `app/infrastructure/email.py` |
| `app/cache.py` | `app/infrastructure/cache.py` |
| `app/cache_keys.py` | `app/infrastructure/cache_keys.py` |
| `app/enums.py` | Split into `app/domains/*/enums.py` per domain |
| `app/utils/` | `app/shared/utils.py` |

## Composable Filter Functions

Each domain gets a `filters.py` with pure functions that transform a SQLAlchemy `Select` statement.

### Pattern

```python
# app/domains/item/filters.py

from sqlalchemy import Select, func
from app.domains.item.models import Item

def available(stmt: Select) -> Select:
    """Only items that are not blocked and have no active loan."""
    return stmt.where(Item.available == True)

def owned_by(stmt: Select, user_id: int) -> Select:
    return stmt.where(Item.owner_id == user_id)

def not_owned_by(stmt: Select, user_id: int) -> Select:
    return stmt.where(Item.owner_id != user_id)

def matching_words(stmt: Select, words: str) -> Select:
    """Trigram similarity search. Adds words_match column, filters, and orders."""
    match_pct = func.similarity(Item.searchable_text, func.normalize_text(words))
    return (
        stmt
        .add_columns(match_pct.label("words_match"))
        .where(match_pct > 0.1)
        .order_by(match_pct.desc())
    )

def in_regions(stmt: Select, region_ids: list[int]) -> Select:
    return stmt.where(Item.regions.any(Region.id.in_(region_ids)))

def in_categories(stmt: Select, category_ids: list[int]) -> Select:
    return stmt.where(Item.categories.any(Category.id.in_(category_ids)))

def with_liked_flag(stmt: Select, user_id: int) -> Select:
    """Add a 'liked' boolean column for the given user."""
    liked_subq = (
        select(literal(True))
        .where(ItemLike.item_id == Item.id)
        .where(ItemLike.user_id == user_id)
        .correlate(Item)
        .exists()
    )
    return stmt.add_columns(liked_subq.label("liked"))

def with_saved_flag(stmt: Select, user_id: int) -> Select:
    """Add a 'saved' boolean column for the given user."""
    saved_subq = (
        select(literal(True))
        .where(ItemSave.item_id == Item.id)
        .where(ItemSave.user_id == user_id)
        .correlate(Item)
        .exists()
    )
    return stmt.add_columns(saved_subq.label("saved"))
```

### Usage in Services

```python
# app/domains/item/services.py

from app.domains.item import filters as item_filters
from app.shared.filters import paginate, order_by_newest

async def list_items(
    db: AsyncSession,
    *,
    words: str | None = None,
    region_ids: list[int] | None = None,
    category_ids: list[int] | None = None,
    available_only: bool = False,
    viewer_id: int | None = None,
    page: PageParams,
) -> PageResult[ItemPreview]:
    stmt = select(Item)

    if words:
        stmt = item_filters.matching_words(stmt, words)
    else:
        stmt = order_by_newest(stmt)

    if available_only:
        stmt = item_filters.available(stmt)
    if region_ids:
        stmt = item_filters.in_regions(stmt, region_ids)
    if category_ids:
        stmt = item_filters.in_categories(stmt, category_ids)
    if viewer_id:
        stmt = item_filters.with_liked_flag(stmt, viewer_id)
        stmt = item_filters.with_saved_flag(stmt, viewer_id)

    stmt = paginate(stmt, page)

    result = await db.execute(stmt)
    return build_page_result(result.all(), page)
```

### Shared Filter Helpers

```python
# app/shared/filters.py

from sqlalchemy import Select, func, text

def order_by_newest(stmt: Select) -> Select:
    return stmt.order_by(text("id DESC"))

def paginate(stmt: Select, page: PageParams) -> Select:
    """Cursor-based keyset pagination."""
    if page.cursor:
        stmt = stmt.where(text("id < :cursor")).params(cursor=page.cursor)
    return stmt.limit(page.limit + 1)  # +1 to detect next page
```

### Testing Filters

Filters are testable in isolation without hitting the DB:

```python
# tests/domains/item/test_filters.py

def test_available_filter():
    stmt = select(Item)
    filtered = available(stmt)
    compiled = str(filtered.compile(compile_kwargs={"literal_binds": True}))
    assert "available = true" in compiled.lower()

def test_matching_words_adds_similarity():
    stmt = select(Item)
    filtered = matching_words(stmt, "stroller")
    compiled = str(filtered.compile(compile_kwargs={"literal_binds": True}))
    assert "similarity" in compiled.lower()
```

Or with integration tests against a real DB session (existing pattern).

## Schema Consolidation

### Principles

1. **Flat, not inherited** -- each schema declares exactly its fields. No deep `Base -> Create -> Read` chains.
2. **Four schemas max per domain**: `Create`, `Update`, `Read`, `Preview`. Not all domains need all four.
3. **Query parameter schemas live in routers**, not in domains (they are an HTTP delivery concern).
4. **Shared pagination schemas** live in `app/shared/pagination.py`.

### Example: Item Domain

```python
# app/domains/item/schemas.py

from pydantic import BaseModel, Field
from datetime import datetime

class ItemCreate(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=2000)
    image_ids: list[int]
    region_ids: list[int]
    category_ids: list[int]

class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    blocked: bool | None = None

class ItemRead(BaseModel):
    id: int
    name: str
    description: str
    blocked: bool
    available: bool
    owner: UserPreview
    images: list[ImageRead]
    regions: list[RegionRead]
    categories: list[CategoryRead]
    liked: bool | None = None
    saved: bool | None = None
    created_at: datetime

class ItemPreview(BaseModel):
    id: int
    name: str
    first_image_name: str | None
    available: bool
    liked: bool | None = None
    saved: bool | None = None
```

### Query Params in Routers

```python
# app/routers/v1/items/queries.py

from pydantic import BaseModel
from app.shared.pagination import PageParams
from app.domains.item.enums import ItemQueryAvailability

class ItemListQuery(BaseModel):
    words: str | None = None
    available: ItemQueryAvailability = ItemQueryAvailability.ALL
    region_ids: list[int] | None = None
    category_ids: list[int] | None = None
    page: PageParams = PageParams()
```

## Cross-Domain Dependency Rules

### Rule 1: Import only from a domain's public API

```python
# Good
from app.domains.user.services import add_stars

# Bad -- reaching into internal module
from app.domains.user.services.star import _compute_star_bonus
```

Each domain's `__init__.py` exports its public surface (models, schemas, key service functions, errors).

### Rule 2: Allowed dependency directions

```
item   -> user (add stars, check ownership)
item   -> image (validate images exist and are owned)
item   -> region (validate regions exist)
item   -> category (validate categories exist)
chat   -> item (get item for chat context)
chat   -> loan (get loan request for message types)
chat   -> user (get user info for messages)
loan   -> item (verify item exists/is available)
auth   -> user (get/create user, validate credentials)
report -> user, item, chat (report targets)
```

No cycles allowed. If a cycle appears, extract shared logic to `app/shared/`.

### Rule 3: Shared session, explicit calls

All cross-domain calls receive the same `db: AsyncSession`. Single transaction. No indirection.

```python
# app/domains/item/services.py

from app.domains.user.services import add_stars
from app.domains.image.services import check_image_owners

async def create_item(db: AsyncSession, owner_id: int, data: ItemCreate) -> Item:
    await check_image_owners(db, data.image_ids, owner_id)
    item = Item(owner_id=owner_id, name=data.name, description=data.description)
    db.add(item)
    await db.flush()
    await add_stars(db, owner_id, stars_gain_when_adding_item(1))
    return item
```

## Infrastructure Layer

### What moves to `app/infrastructure/`

| Module | Responsibility |
|---|---|
| `database.py` | `create_session_maker()`, `get_db_session()` dependency, `init_db_session_dependency()` |
| `cache.py` | `Cache` class, `NullCache`, `get_cache()` dependency |
| `cache_keys.py` | Cache key builder functions |
| `redis.py` | `create_redis_client()` factory |
| `pubsub.py` | `Broadcast` wrapper, `get_broadcast()`, `notify_user_after_commit()`, `flush_pending_notifications()` |
| `email.py` | `FastMail` wrapper, `get_email_client()` dependency |
| `storage.py` | S3/MinIO client (from `clients/storage/`) |
| `config.py` | `Config` and all sub-configs (`DatabaseConfig`, `RedisConfig`, etc.) |

### What moves to `app/shared/`

| Module | Responsibility |
|---|---|
| `pagination.py` | `PageParams`, `PageResult`, `QueryPageCursor`, cursor helpers, `set_response_headers()` |
| `schemas.py` | Shared Pydantic base model if needed |
| `filters.py` | Generic `paginate()`, `order_by_newest()`, `with_total_count()` |
| `utils.py` | `integer_range_to_inclusive()`, hash helpers, other pure utilities |

## Shared Pagination

```python
# app/shared/pagination.py

from pydantic import BaseModel

class PageParams(BaseModel):
    limit: int = 32
    cursor: int | None = None

class PageResult(BaseModel, Generic[T]):
    data: list[T]
    next_cursor: int | None = None
    total_count: int | None = None

    def set_response_headers(self, response: Response, request: Request):
        if self.total_count is not None:
            response.headers["X-Total-Count"] = str(self.total_count)
        if self.next_cursor is not None:
            # build Link header for next page
            ...
```

```python
# app/shared/filters.py

def paginate(stmt: Select, page: PageParams) -> Select:
    if page.cursor:
        stmt = stmt.where(text("id < :cursor")).params(cursor=page.cursor)
    return stmt.limit(page.limit + 1)

def build_page_result(rows: list, page: PageParams) -> PageResult:
    has_next = len(rows) > page.limit
    data = rows[:page.limit]
    next_cursor = data[-1].id if has_next and data else None
    return PageResult(data=data, next_cursor=next_cursor)
```

## Models

Models stay as SQLAlchemy ORM models. No changes to model definitions, only to where they live.

- `app/models/base.py` -> `app/shared/models.py` for `Base`, `IntegerIdentifier`, `CreationDate`, `UpdateDate` mixins
- Each domain's `models.py` imports from `app.shared.models`

```python
# app/shared/models.py

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class IntegerIdentifier:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

class CreationDate:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

class UpdateDate:
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now(), nullable=True)
```

## Router Changes

Routers stay structurally the same. Only import paths change:

```python
# Before
from app.services.item.read.list import list_items
from app.schemas.item.read import ItemPreviewRead

# After
from app.domains.item.services import list_items
from app.domains.item.schemas import ItemPreview
```

Query parameter schemas move from `app/schemas/` to `app/routers/v1/*/queries.py`.

## Test Structure

```
tests/
  domains/
    item/
      test_filters.py        # filter functions in isolation
      test_services.py       # integration tests (or split by operation)
      test_create.py
      test_read.py
      test_update.py
      test_delete.py
      test_like.py
      test_save.py
    chat/
      test_filters.py
      test_text.py
      test_non_text.py
      test_permissions.py
      test_seen.py
    loan/
      test_request_create.py
      test_request_read.py
      ...
    user/
      ...
    auth/
      test_auth.py
  routers/                   # if needed for router-specific tests
    ...
  infrastructure/
    test_cache.py
    test_websocket.py
    test_s3.py
    ...
  fixtures/                  # stays as-is
    database.py
    app.py
    users.py
    items.py
    ...
  conftest.py
  utils.py
```

## Migration Strategy

All work on a dedicated branch. Mechanical restructure first, then refactor.

### Phase 1: Mechanical Move (tests must pass after each step)

1. Create `app/domains/` directory structure
2. Move models from `app/models/` to `app/domains/*/models.py`
3. Update `app/models/__init__.py` to re-export from new locations (Alembic compatibility)
4. Move errors from `app/errors/` to `app/domains/*/errors.py`
5. Move schemas from `app/schemas/` to `app/domains/*/schemas.py`
6. Extract query param schemas to `app/routers/v1/*/queries.py`
7. Move services from `app/services/` to `app/domains/*/services.py`
8. Absorb `app/clients/database/` into relevant domain services
9. Move infrastructure modules to `app/infrastructure/`
10. Move shared utilities to `app/shared/`
11. Update all imports across routers, tests, and Alembic config
12. Delete old empty directories
13. Restructure tests to mirror new layout

### Phase 2: Refactor Query Logic

14. For each domain, extract filter functions from services into `filters.py`
15. Refactor `list_*` service functions to compose filters
16. Extract shared pagination/ordering helpers to `app/shared/filters.py`
17. Add filter unit tests

### Phase 3: Schema Consolidation

18. Flatten schema inheritance per domain
19. Remove redundant intermediate schemas
20. Ensure router response models reference new schemas

### Phase 4: Cleanup

21. Remove all backward-compatibility re-exports
22. Run full lint (`mise run lint`) and fix
23. Run full test suite (`mise run test`) and fix
24. Review cross-domain imports for rule violations

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Alembic can't find models after move | Migrations break | Keep `app/models/__init__.py` re-exporting from `app/domains/` during migration; update Alembic `env.py` target_metadata |
| Mass import changes cause merge conflicts | Blocks other work | Dedicated branch, merge quickly, coordinate |
| Circular imports from cross-domain calls | Import errors | Follow dependency direction rules; use late imports only as last resort |
| `filters.py` doesn't cover all current query patterns | Incomplete migration | Audit each service's query logic; some complex queries may stay inline initially |
| Test restructure breaks pytest discovery | Tests don't run | Keep `conftest.py` and fixture paths stable; update `pytest_plugins` list |

## Success Criteria

- All existing tests pass with no behavior changes
- Each domain is self-contained in `app/domains/{name}/`
- No service imports SQLAlchemy constructs that should be in a filter function
- Query param schemas live in routers, not domains
- Cross-domain imports follow the allowed dependency graph
- `mise run lint` and `mise run test` pass clean
