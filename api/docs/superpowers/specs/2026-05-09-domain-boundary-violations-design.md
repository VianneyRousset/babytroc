# Domain Boundary Violations Fix

**Date:** 2026-05-09
**Status:** Draft
**Branch:** refactor/ddd-lite-restructure (continues from DDD-lite restructure)

## Problem Statement

After the DDD-lite restructure, 10 cross-domain write boundary violations remain:

1. **loan → chat** (6 violations): loan services import `send_many_chat_messages`/`send_chat_message` from chat to generate messages on loan state changes
2. **item → user** (2 violations): item create imports `add_many_stars_to_users` from user to award stars
3. **auth → user** (1 violation): auth validation imports `invalidate_user_validated` from user cache
4. **Region/Category models** in item domain: forces region/category services to import from item

Additionally, the dependency graph needs to explicitly allow read-only cross-domain model imports (user reading Item/ItemLike for profiles, image reading User for ownership validation).

## Goals

- Zero violations from `python scripts/check_domain_boundaries.py`
- All cross-domain write side effects go through a typed event bus
- Region and Category ORM models live in their own domains
- Explicit documented rule: any domain may read-query any other domain's models

## Non-Goals

- External message queue or async event processing
- CQRS or event sourcing
- Changing the existing QueryFilter class hierarchy
- Restructuring the pubsub/websocket notification system (only moving schemas)

## Architectural Rule: Read vs. Write Boundaries

**Reads (allowed across domains):**
- Any domain can import and query any other domain's models (SELECT)
- Any domain can import read/get/list functions from another domain's services

**Writes (must use events):**
- Creating, updating, or deleting data in another domain must go through events
- The owning domain's service performs the write, triggered by an event handler

**Exception:**
- `handlers.py` files are the official cross-domain write path (exempt from boundary check)
- Direct cross-domain writes are allowed where the dependency is structural and one-directional (e.g., auth→user for creating users, loan→item for checking item availability)

## Event Bus Design

### Location

`app/infrastructure/events.py` — module-level singleton, ~30 LOC.

### Implementation

```python
from dataclasses import dataclass
from collections import defaultdict
from typing import Any, Awaitable, Callable
import logging

logger = logging.getLogger(__name__)

type EventHandler = Callable[[Any, Any], Awaitable[None]]

@dataclass
class _Registration:
    handler: EventHandler
    critical: bool

_handlers: dict[type, list[_Registration]] = defaultdict(list)

def on(event_type: type, *, critical: bool = True):
    """Register a handler for an event type."""
    def decorator(fn: EventHandler):
        _handlers[event_type].append(_Registration(handler=fn, critical=critical))
        return fn
    return decorator

async def emit(db, event: object):
    """Dispatch event to all registered handlers.

    Critical handlers propagate exceptions (rolling back the transaction).
    Non-critical handlers log and swallow exceptions.
    """
    for reg in _handlers[type(event)]:
        if reg.critical:
            await reg.handler(db, event)
        else:
            try:
                await reg.handler(db, event)
            except Exception:
                logger.exception(
                    "Non-critical handler %s failed for %s",
                    reg.handler.__name__,
                    type(event).__name__,
                )
```

### Properties

- Handlers run in registration order (order of import)
- Same `db: AsyncSession` passed to all handlers (same transaction)
- `critical=True` (default): exception propagates, rolls back entire transaction
- `critical=False`: exception caught and logged, main operation succeeds
- No queue, no thread — just function call indirection
- Handlers registered at import time via `@on` decorator
- Handler modules imported in `app/app.py` at startup

## Event Definitions

Events are frozen dataclasses defined in the domain that emits them.

### app/domains/item/events.py

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ItemCreated:
    item_id: int
    owner_id: int

@dataclass(frozen=True)
class ItemUpdated:
    item_id: int
    owner_id: int

@dataclass(frozen=True)
class ItemDeleted:
    item_id: int
    owner_id: int

@dataclass(frozen=True)
class ItemLiked:
    item_id: int
    user_id: int

@dataclass(frozen=True)
class ItemUnliked:
    item_id: int
    user_id: int

@dataclass(frozen=True)
class ItemSaved:
    item_id: int
    user_id: int

@dataclass(frozen=True)
class ItemUnsaved:
    item_id: int
    user_id: int
```

### app/domains/loan/events.py

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class LoanRequestCreated:
    loan_request_id: int
    item_id: int
    borrower_id: int
    owner_id: int

@dataclass(frozen=True)
class LoanRequestAccepted:
    loan_request_id: int
    item_id: int
    borrower_id: int
    owner_id: int

@dataclass(frozen=True)
class LoanRequestRejected:
    loan_request_id: int
    item_id: int
    borrower_id: int
    owner_id: int

@dataclass(frozen=True)
class LoanRequestCancelled:
    loan_request_id: int
    item_id: int
    borrower_id: int
    owner_id: int

@dataclass(frozen=True)
class LoanStarted:
    loan_id: int
    loan_request_id: int
    item_id: int
    borrower_id: int
    owner_id: int

@dataclass(frozen=True)
class LoanEnded:
    loan_id: int
    item_id: int
    borrower_id: int
    owner_id: int
```

### app/domains/auth/events.py

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AccountValidated:
    user_id: int
```

## Handlers

### app/domains/chat/handlers.py

Handles loan state → chat message generation and account validation → pubsub notification.

```python
from app.infrastructure.events import on
from app.domains.loan.events import (
    LoanRequestCreated, LoanRequestAccepted, LoanRequestRejected,
    LoanRequestCancelled, LoanStarted, LoanEnded,
)
from app.domains.auth.events import AccountValidated

@on(LoanRequestCreated)
async def send_loan_request_created_message(db, event):
    # Construct and send chat message using chat.services.message.create
    ...

@on(LoanRequestAccepted)
async def send_loan_request_accepted_message(db, event):
    ...

@on(LoanRequestRejected)
async def send_loan_request_rejected_message(db, event):
    ...

@on(LoanRequestCancelled)
async def send_loan_request_cancelled_message(db, event):
    ...

@on(LoanStarted)
async def send_loan_started_message(db, event):
    ...

@on(LoanEnded)
async def send_loan_ended_message(db, event):
    ...

@on(AccountValidated)
async def send_account_validated_notification(db, event):
    # Send pubsub notification to user
    ...
```

### app/domains/user/handlers.py

Handles item created → star award and user cache invalidation.

```python
from app.infrastructure.events import on
from app.domains.item.events import ItemCreated
from app.domains.auth.events import AccountValidated

@on(ItemCreated)
async def award_stars_on_item_created(db, event):
    from app.domains.user.services.star.update import add_many_stars_to_users
    from app.domains.user.star import stars_gain_when_adding_item
    await add_many_stars_to_users(db, {event.owner_id: stars_gain_when_adding_item(1)})

@on(AccountValidated, critical=False)
async def invalidate_user_cache_on_validation(db, event):
    from app.infrastructure.cache import get_cache
    from app.infrastructure.cache_keys import key_user
    cache = get_cache()
    await cache.delete(key_user(event.user_id))
```

### app/domains/item/handlers.py

Handles cache invalidation for item events.

```python
from app.infrastructure.events import on
from app.domains.item.events import (
    ItemCreated, ItemUpdated, ItemDeleted,
    ItemLiked, ItemUnliked, ItemSaved, ItemUnsaved,
)

@on(ItemCreated, critical=False)
async def invalidate_cache_on_create(db, event):
    from app.domains.item.services.cache import invalidate_item_created
    from app.infrastructure.cache import get_cache
    await invalidate_item_created(get_cache(), owner_id=event.owner_id)

@on(ItemUpdated, critical=False)
async def invalidate_cache_on_update(db, event):
    from app.domains.item.services.cache import invalidate_item_updated
    from app.infrastructure.cache import get_cache
    await invalidate_item_updated(get_cache(), item_id=event.item_id, owner_id=event.owner_id)

@on(ItemDeleted, critical=False)
async def invalidate_cache_on_delete(db, event):
    from app.domains.item.services.cache import invalidate_item_deleted
    from app.infrastructure.cache import get_cache
    await invalidate_item_deleted(get_cache(), item_id=event.item_id, owner_id=event.owner_id)

@on(ItemLiked, critical=False)
async def invalidate_cache_on_like(db, event):
    from app.domains.item.services.cache import invalidate_item_liked
    from app.infrastructure.cache import get_cache
    await invalidate_item_liked(get_cache(), item_id=event.item_id, liker_id=event.user_id)

@on(ItemUnliked, critical=False)
async def invalidate_cache_on_unlike(db, event):
    from app.domains.item.services.cache import invalidate_item_liked
    from app.infrastructure.cache import get_cache
    await invalidate_item_liked(get_cache(), item_id=event.item_id, liker_id=event.user_id)

@on(ItemSaved, critical=False)
async def invalidate_cache_on_save(db, event):
    from app.domains.item.services.cache import invalidate_item_saved
    from app.infrastructure.cache import get_cache
    await invalidate_item_saved(get_cache(), saver_id=event.user_id)

@on(ItemUnsaved, critical=False)
async def invalidate_cache_on_unsave(db, event):
    from app.domains.item.services.cache import invalidate_item_saved
    from app.infrastructure.cache import get_cache
    await invalidate_item_saved(get_cache(), saver_id=event.user_id)
```

### app/domains/loan/handlers.py

Handles cache invalidation for loan events.

```python
from app.infrastructure.events import on
from app.domains.loan.events import (
    LoanRequestCreated, LoanRequestAccepted, LoanRequestRejected,
    LoanRequestCancelled, LoanStarted, LoanEnded,
)

@on(LoanRequestCreated, critical=False)
async def invalidate_cache_on_request_created(db, event):
    from app.domains.loan.services.cache import invalidate_loan_request_created
    from app.infrastructure.cache import get_cache
    await invalidate_loan_request_created(get_cache(), item_id=event.item_id, borrower_id=event.borrower_id)

# Similar handlers for other loan events that need cache invalidation
```

## Handler Registration

All handler modules are imported at app startup in `app/app.py`:

```python
# app/app.py (near top, after other imports)
import app.domains.chat.handlers  # noqa: F401
import app.domains.user.handlers  # noqa: F401
import app.domains.item.handlers  # noqa: F401
import app.domains.loan.handlers  # noqa: F401
```

## Model Relocation: Region and Category

### Region

Move `Region` ORM model from `app/domains/item/models/region.py` to `app/domains/region/models.py`.

Keep `ItemRegionAssociation` in `app/domains/item/models/region.py` — it expresses the item↔region relationship and imports `Region` from the region domain.

### Category

Move `Category` ORM model from `app/domains/item/models/category.py` to `app/domains/category/models.py`.

Keep `ItemCategoryAssociation` in `app/domains/item/models/category.py` — it imports `Category` from the category domain.

### Alembic Impact

No schema changes — models move between Python files but the underlying tables stay the same. Alembic only cares that models are imported somewhere that registers with `Base.metadata`. Update `app/domains/__init__.py` to import region and category models.

## Service Changes

### Loan services (remove chat imports)

For each loan service that currently imports and calls `send_many_chat_messages`:
1. Remove the import
2. After the main operation, call `await emit(db, LoanRequestAccepted(...))`
3. The chat handler picks it up

Example — `app/domains/loan/services/request/accept.py`:

```python
# Before
from app.domains.chat.services import send_many_chat_messages
# ... later in the function:
await send_many_chat_messages(db, messages, ensure_chats=True)

# After
from app.infrastructure.events import emit
from app.domains.loan.events import LoanRequestAccepted
# ... later in the function:
await emit(db, LoanRequestAccepted(
    loan_request_id=loan_request.id,
    item_id=loan_request.item_id,
    borrower_id=loan_request.borrower_id,
    owner_id=item.owner_id,
))
```

### Item create (remove star import)

```python
# Before
from app.domains.user.services.star import add_many_stars_to_users, AddUserStars
await add_many_stars_to_users(db, ...)

# After
from app.infrastructure.events import emit
from app.domains.item.events import ItemCreated
await emit(db, ItemCreated(item_id=item.id, owner_id=owner_id))
```

### Item like/unlike/save/unsave (remove cache imports)

```python
# Before
from app.domains.item.services.cache import invalidate_item_liked
await invalidate_item_liked(cache, item_id=item_id, liker_id=user_id)

# After
from app.infrastructure.events import emit
from app.domains.item.events import ItemLiked
await emit(db, ItemLiked(item_id=item_id, user_id=user_id))
```

### Auth validation (remove user cache import)

```python
# Before
from app.domains.user.services.cache import invalidate_user_validated
await invalidate_user_validated(cache, user_id=user_id)

# After
from app.infrastructure.events import emit
from app.domains.auth.events import AccountValidated
await emit(db, AccountValidated(user_id=user_id))
```

## Updated Dependency Graph

```
item     → region, category (association models)
loan     → item (check availability — direct call, allowed)
auth     → user (get/create user — direct call, allowed)
image    → user (validate owner — direct call, allowed)
region   → (standalone)
category → (standalone)
chat     → (standalone — reacts to events only)
user     → (standalone — reacts to events only)
report   → user, item, chat (read-only for report targets)
```

**Event flow (no import coupling):**
```
loan emits → chat.handlers, loan.handlers (cache)
item emits → user.handlers (stars), item.handlers (cache)
auth emits → user.handlers (cache), chat.handlers (pubsub)
```

## Testing

### Event bus unit tests

```python
# tests/infrastructure/test_events.py

async def test_emit_calls_handler():
    # Register a handler, emit event, assert handler was called

async def test_critical_handler_propagates_exception():
    # Register a critical handler that raises, assert emit raises

async def test_non_critical_handler_swallows_exception():
    # Register non-critical handler that raises, assert emit succeeds

async def test_multiple_handlers_run_in_order():
    # Register two handlers, assert both called in order
```

### Handler integration tests

Existing tests (e.g., loan request acceptance tests) already verify end-to-end behavior (loan accepted → chat message appears). These should continue passing unchanged since the event bus is transparent — same transaction, same outcome.

### Boundary check in CI

```bash
python scripts/check_domain_boundaries.py
```

Must exit 0 after all changes.

## Migration Strategy

1. Implement event bus (`app/infrastructure/events.py`)
2. Define all event dataclasses
3. Write all handlers
4. Register handlers in `app/app.py`
5. One domain at a time: replace direct cross-domain write calls with `emit()` calls
6. Move Region/Category models
7. Run `scripts/check_domain_boundaries.py` — verify 0 violations
8. Run full test suite — verify all 275 tests pass

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Handler ordering matters for correctness | Subtle bugs if handlers depend on each other | Keep handlers independent — each should work regardless of order |
| Debugging "what happens when X" requires checking handlers | Slower investigation | Name handlers descriptively; grep for `@on(EventType)` to find all reactions |
| Non-critical handler failures go unnoticed | Stale cache | Structured logging with monitoring/alerting on handler failures |
| Chat message handler needs data not in the event | Handler has to re-query | Include all needed IDs in event dataclass; handler queries what it needs from db |
| Circular handler chains (event A triggers handler that emits event B that triggers...) | Infinite loops | Rule: handlers MUST NOT emit new events. They may call same-domain services directly. If cross-domain event chaining is needed, revisit design. |

## Boundary Check Script Update

Update `scripts/check_domain_boundaries.py` to support an allowlist for structural dependencies that are intentional direct cross-domain writes:

```python
ALLOWED_CROSS_DOMAIN_WRITES = {
    ("auth", "user"),   # auth creates users, validates credentials
    ("loan", "item"),   # loan checks item availability
}
```

The script skips violations for these (source_domain, target_domain) pairs. All other cross-domain writes must go through events.

## Success Criteria

- `python scripts/check_domain_boundaries.py` exits 0
- All 275 existing tests pass with no behavior changes
- Event bus has its own unit tests
- No domain service imports write functions from another domain (except explicit structural deps: auth→user, loan→item)
- Region model lives in region domain, Category in category domain
