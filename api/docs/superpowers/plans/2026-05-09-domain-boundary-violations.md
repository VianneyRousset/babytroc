# Domain Boundary Violations Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate all cross-domain write boundary violations by introducing a minimal event bus and relocating models, achieving 0 violations from `scripts/check_domain_boundaries.py`.

**Architecture:** A 30-LOC in-process event bus (`emit`/`on`) lets domains emit events after their main operations. Handler modules in other domains react to these events (same transaction). Region/Category models move to their own domains. Cache invalidation becomes non-critical event handlers.

**Tech Stack:** Python 3.13, SQLAlchemy async, dataclasses (events), pytest

**Spec:** `docs/superpowers/specs/2026-05-09-domain-boundary-violations-design.md`

---

## Task 1: Implement the event bus

**Files:**
- Create: `app/infrastructure/events.py`
- Test: `tests/infrastructure/test_events.py`

- [ ] **Step 1: Write tests for the event bus**

```python
# tests/infrastructure/test_events.py

from dataclasses import dataclass

import pytest

from app.infrastructure.events import _handlers, emit, on


@dataclass(frozen=True)
class _TestEvent:
    value: int


@dataclass(frozen=True)
class _UnhandledEvent:
    pass


@pytest.fixture(autouse=True)
def _clear_handlers():
    """Clear event handlers before and after each test."""
    _handlers.clear()
    yield
    _handlers.clear()


async def test_emit_calls_registered_handler():
    results = []

    @on(_TestEvent)
    async def handler(db, event):
        results.append(event.value)

    await emit(None, _TestEvent(value=42))
    assert results == [42]


async def test_emit_with_no_handlers_does_nothing():
    await emit(None, _UnhandledEvent())


async def test_multiple_handlers_run_in_order():
    results = []

    @on(_TestEvent)
    async def first(db, event):
        results.append("first")

    @on(_TestEvent)
    async def second(db, event):
        results.append("second")

    await emit(None, _TestEvent(value=1))
    assert results == ["first", "second"]


async def test_critical_handler_propagates_exception():
    @on(_TestEvent, critical=True)
    async def failing(db, event):
        msg = "boom"
        raise RuntimeError(msg)

    with pytest.raises(RuntimeError, match="boom"):
        await emit(None, _TestEvent(value=1))


async def test_non_critical_handler_swallows_exception(caplog):
    results = []

    @on(_TestEvent, critical=False)
    async def failing(db, event):
        msg = "non-critical failure"
        raise RuntimeError(msg)

    @on(_TestEvent)
    async def after(db, event):
        results.append("ran")

    await emit(None, _TestEvent(value=1))
    assert results == ["ran"]
    assert "non-critical failure" in caplog.text


async def test_handler_receives_db_session():
    received_db = []

    @on(_TestEvent)
    async def handler(db, event):
        received_db.append(db)

    sentinel = object()
    await emit(sentinel, _TestEvent(value=1))
    assert received_db == [sentinel]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/infrastructure/test_events.py -v
```

Expected: FAIL (module does not exist yet)

- [ ] **Step 3: Implement the event bus**

```python
# app/infrastructure/events.py

import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

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


async def emit(db: Any, event: object) -> None:
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

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/infrastructure/test_events.py -v
```

Expected: all 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add app/infrastructure/events.py tests/infrastructure/test_events.py
git commit -m "feat: add minimal typed event bus"
```

---

## Task 2: Define event dataclasses

**Files:**
- Create: `app/domains/item/events.py`
- Create: `app/domains/loan/events.py`
- Create: `app/domains/auth/events.py`

- [ ] **Step 1: Create item events**

```python
# app/domains/item/events.py

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
    item_owner_id: int


@dataclass(frozen=True)
class ItemUnliked:
    item_id: int
    user_id: int
    item_owner_id: int


@dataclass(frozen=True)
class ItemSaved:
    item_id: int
    user_id: int


@dataclass(frozen=True)
class ItemUnsaved:
    item_id: int
    user_id: int
```

- [ ] **Step 2: Create loan events**

```python
# app/domains/loan/events.py

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

- [ ] **Step 3: Create auth events**

```python
# app/domains/auth/events.py

from dataclasses import dataclass


@dataclass(frozen=True)
class AccountValidated:
    user_id: int
```

- [ ] **Step 4: Verify imports work**

```bash
python -c "from app.domains.item.events import ItemCreated; from app.domains.loan.events import LoanRequestCreated; from app.domains.auth.events import AccountValidated; print('OK')"
```

- [ ] **Step 5: Commit**

```bash
git add app/domains/item/events.py app/domains/loan/events.py app/domains/auth/events.py
git commit -m "feat: define domain event dataclasses"
```

---

## Task 3: Create chat handlers (loan→chat decoupling)

This is the biggest handler — it replaces all 6 `send_many_chat_messages` calls in loan services.

**Files:**
- Create: `app/domains/chat/handlers.py`

- [ ] **Step 1: Create the chat handlers module**

Read the existing loan service code to understand what chat messages are sent for each loan event. The handlers must replicate exactly this behavior.

Each loan service currently:
1. Constructs a `SendChatMessage*` schema (from `app/domains/chat/schemas/send.py`)
2. Calls `send_many_chat_messages(db, messages=[...], ensure_chats=...)` or `send_chat_message(db, message=...)`

The handlers will do the same, importing from within the chat domain.

```python
# app/domains/chat/handlers.py

from app.infrastructure.events import on
from app.domains.loan.events import (
    LoanRequestAccepted,
    LoanRequestCancelled,
    LoanRequestCreated,
    LoanRequestRejected,
    LoanStarted,
    LoanEnded,
)
from app.domains.auth.events import AccountValidated


@on(LoanRequestCreated)
async def send_loan_request_created_message(db, event: LoanRequestCreated):
    from app.domains.chat.schemas.base import ChatId
    from app.domains.chat.schemas.send import SendChatMessageLoanRequestCreated
    from app.domains.chat.services.message.create import send_many_chat_messages

    await send_many_chat_messages(
        db=db,
        messages=[
            SendChatMessageLoanRequestCreated(
                chat_id=ChatId.from_values(
                    item_id=event.item_id,
                    borrower_id=event.borrower_id,
                ),
                loan_request_id=event.loan_request_id,
            )
        ],
        ensure_chats=True,
    )


@on(LoanRequestAccepted)
async def send_loan_request_accepted_message(db, event: LoanRequestAccepted):
    from app.domains.chat.schemas.base import ChatId
    from app.domains.chat.schemas.send import SendChatMessageLoanRequestAccepted
    from app.domains.chat.services.message.create import send_many_chat_messages

    await send_many_chat_messages(
        db=db,
        messages=[
            SendChatMessageLoanRequestAccepted(
                chat_id=ChatId.from_values(
                    item_id=event.item_id,
                    borrower_id=event.borrower_id,
                ),
                loan_request_id=event.loan_request_id,
            )
        ],
    )


@on(LoanRequestRejected)
async def send_loan_request_rejected_message(db, event: LoanRequestRejected):
    from app.domains.chat.schemas.base import ChatId
    from app.domains.chat.schemas.send import SendChatMessageLoanRequestRejected
    from app.domains.chat.services.message.create import send_many_chat_messages

    await send_many_chat_messages(
        db=db,
        messages=[
            SendChatMessageLoanRequestRejected(
                chat_id=ChatId.from_values(
                    item_id=event.item_id,
                    borrower_id=event.borrower_id,
                ),
                loan_request_id=event.loan_request_id,
            )
        ],
    )


@on(LoanRequestCancelled)
async def send_loan_request_cancelled_message(db, event: LoanRequestCancelled):
    from app.domains.chat.schemas.base import ChatId
    from app.domains.chat.schemas.send import SendChatMessageLoanRequestCancelled
    from app.domains.chat.services.message.create import send_many_chat_messages

    await send_many_chat_messages(
        db=db,
        messages=[
            SendChatMessageLoanRequestCancelled(
                chat_id=ChatId.from_values(
                    item_id=event.item_id,
                    borrower_id=event.borrower_id,
                ),
                loan_request_id=event.loan_request_id,
            )
        ],
    )


@on(LoanStarted)
async def send_loan_started_message(db, event: LoanStarted):
    from app.domains.chat.schemas.base import ChatId
    from app.domains.chat.schemas.send import SendChatMessageLoanStarted
    from app.domains.chat.services.message.create import send_many_chat_messages

    await send_many_chat_messages(
        db=db,
        messages=[
            SendChatMessageLoanStarted(
                chat_id=ChatId.from_values(
                    item_id=event.item_id,
                    borrower_id=event.borrower_id,
                ),
                loan_id=event.loan_id,
            )
        ],
    )


@on(LoanEnded)
async def send_loan_ended_message(db, event: LoanEnded):
    from app.domains.chat.schemas.base import ChatId
    from app.domains.chat.schemas.send import SendChatMessageLoanEnded
    from app.domains.chat.services.message.create import send_many_chat_messages

    await send_many_chat_messages(
        db=db,
        messages=[
            SendChatMessageLoanEnded(
                chat_id=ChatId.from_values(
                    item_id=event.item_id,
                    borrower_id=event.borrower_id,
                ),
                loan_id=event.loan_id,
            )
        ],
    )


@on(AccountValidated)
async def send_account_validated_notification(db, event: AccountValidated):
    from app.domains.chat.schemas.pubsub import PubsubMessageUpdatedAccountValidation
    from app.infrastructure.pubsub import get_broadcast, notify_user_after_commit

    notify_user_after_commit(
        db=db,
        broadcast=get_broadcast(),
        user_id=event.user_id,
        message=PubsubMessageUpdatedAccountValidation(validated=True),
    )
```

- [ ] **Step 2: Commit**

```bash
git add app/domains/chat/handlers.py
git commit -m "feat: add chat event handlers for loan and auth events"
```

---

## Task 4: Create user and item handlers

**Files:**
- Create: `app/domains/user/handlers.py`
- Create: `app/domains/item/handlers.py`

- [ ] **Step 1: Create user handlers (star award + cache invalidation)**

```python
# app/domains/user/handlers.py

from app.infrastructure.events import on
from app.domains.auth.events import AccountValidated
from app.domains.item.events import ItemCreated


@on(ItemCreated)
async def award_stars_on_item_created(db, event: ItemCreated):
    from app.domains.user.services.star import AddUserStars, add_many_stars_to_users
    from app.domains.user.star import stars_gain_when_adding_item

    await add_many_stars_to_users(
        db=db,
        user_stars={
            AddUserStars(
                user_id=event.owner_id,
                stars=stars_gain_when_adding_item(1),
            )
        },
    )


@on(AccountValidated, critical=False)
async def invalidate_user_cache_on_validation(db, event: AccountValidated):
    from app.infrastructure.cache import get_cache
    from app.domains.user.services.cache import invalidate_user_validated

    cache = get_cache()
    await invalidate_user_validated(cache, user_id=event.user_id)
```

- [ ] **Step 2: Create item handlers (cache invalidation)**

```python
# app/domains/item/handlers.py

from app.infrastructure.events import on
from app.domains.item.events import (
    ItemCreated,
    ItemDeleted,
    ItemLiked,
    ItemSaved,
    ItemUnliked,
    ItemUnsaved,
    ItemUpdated,
)


@on(ItemCreated, critical=False)
async def invalidate_cache_on_item_created(db, event: ItemCreated):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_created

    await invalidate_item_created(get_cache(), owner_id=event.owner_id)


@on(ItemUpdated, critical=False)
async def invalidate_cache_on_item_updated(db, event: ItemUpdated):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_updated

    await invalidate_item_updated(get_cache(), item_id=event.item_id, owner_id=event.owner_id)


@on(ItemDeleted, critical=False)
async def invalidate_cache_on_item_deleted(db, event: ItemDeleted):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_deleted

    await invalidate_item_deleted(get_cache(), item_id=event.item_id, owner_id=event.owner_id)


@on(ItemLiked, critical=False)
async def invalidate_cache_on_item_liked(db, event: ItemLiked):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_liked

    await invalidate_item_liked(get_cache(), liker_id=event.user_id, item_owner_id=event.item_owner_id)


@on(ItemUnliked, critical=False)
async def invalidate_cache_on_item_unliked(db, event: ItemUnliked):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_liked

    await invalidate_item_liked(get_cache(), liker_id=event.user_id, item_owner_id=event.item_owner_id)


@on(ItemSaved, critical=False)
async def invalidate_cache_on_item_saved(db, event: ItemSaved):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_saved

    await invalidate_item_saved(get_cache(), saver_id=event.user_id)


@on(ItemUnsaved, critical=False)
async def invalidate_cache_on_item_unsaved(db, event: ItemUnsaved):
    from app.infrastructure.cache import get_cache
    from app.domains.item.services.cache import invalidate_item_saved

    await invalidate_item_saved(get_cache(), saver_id=event.user_id)
```

- [ ] **Step 3: Commit**

```bash
git add app/domains/user/handlers.py app/domains/item/handlers.py
git commit -m "feat: add user and item event handlers"
```

---

## Task 5: Create loan handlers (cache invalidation)

**Files:**
- Create: `app/domains/loan/handlers.py`

- [ ] **Step 1: Create loan cache invalidation handlers**

```python
# app/domains/loan/handlers.py

from app.infrastructure.events import on
from app.domains.loan.events import (
    LoanEnded,
    LoanRequestAccepted,
    LoanRequestCancelled,
    LoanRequestCreated,
    LoanRequestRejected,
    LoanStarted,
)


@on(LoanRequestCreated, critical=False)
async def invalidate_cache_on_request_created(db, event: LoanRequestCreated):
    from app.infrastructure.cache import get_cache
    from app.domains.loan.services.cache import invalidate_loan_request_created

    await invalidate_loan_request_created(
        get_cache(),
        item_id=event.item_id,
        borrower_id=event.borrower_id,
        owner_id=event.owner_id,
    )


@on(LoanRequestAccepted, critical=False)
async def invalidate_cache_on_request_accepted(db, event: LoanRequestAccepted):
    from app.infrastructure.cache import get_cache
    from app.domains.loan.services.cache import invalidate_loan_request_state_changed

    await invalidate_loan_request_state_changed(
        get_cache(),
        item_id=event.item_id,
        borrower_id=event.borrower_id,
        owner_id=event.owner_id,
    )


@on(LoanRequestRejected, critical=False)
async def invalidate_cache_on_request_rejected(db, event: LoanRequestRejected):
    from app.infrastructure.cache import get_cache
    from app.domains.loan.services.cache import invalidate_loan_request_state_changed

    await invalidate_loan_request_state_changed(
        get_cache(),
        item_id=event.item_id,
        borrower_id=event.borrower_id,
        owner_id=event.owner_id,
    )


@on(LoanRequestCancelled, critical=False)
async def invalidate_cache_on_request_cancelled(db, event: LoanRequestCancelled):
    from app.infrastructure.cache import get_cache
    from app.domains.loan.services.cache import invalidate_loan_request_state_changed

    await invalidate_loan_request_state_changed(
        get_cache(),
        item_id=event.item_id,
        borrower_id=event.borrower_id,
        owner_id=event.owner_id,
    )


@on(LoanStarted, critical=False)
async def invalidate_cache_on_loan_started(db, event: LoanStarted):
    from app.infrastructure.cache import get_cache
    from app.domains.loan.services.cache import invalidate_loan_started

    await invalidate_loan_started(
        get_cache(),
        item_id=event.item_id,
        borrower_id=event.borrower_id,
        owner_id=event.owner_id,
    )


@on(LoanEnded, critical=False)
async def invalidate_cache_on_loan_ended(db, event: LoanEnded):
    from app.infrastructure.cache import get_cache
    from app.domains.loan.services.cache import invalidate_loan_ended

    await invalidate_loan_ended(
        get_cache(),
        item_id=event.item_id,
        borrower_id=event.borrower_id,
        owner_id=event.owner_id,
    )
```

- [ ] **Step 2: Commit**

```bash
git add app/domains/loan/handlers.py
git commit -m "feat: add loan cache invalidation event handlers"
```

---

## Task 6: Register handlers at app startup

**Files:**
- Modify: `app/app.py`

- [ ] **Step 1: Import all handler modules in app.py**

Add these imports near the top of `app/app.py` (after existing imports, before `create_app`):

```python
# Register event handlers
import app.domains.chat.handlers  # noqa: F401
import app.domains.item.handlers  # noqa: F401
import app.domains.loan.handlers  # noqa: F401
import app.domains.user.handlers  # noqa: F401
```

- [ ] **Step 2: Run tests to verify handlers load without error**

```bash
pytest tests/infrastructure/test_events.py -v
```

- [ ] **Step 3: Commit**

```bash
git add app/app.py
git commit -m "feat: register all event handlers at app startup"
```

---

## Task 7: Refactor loan services to emit events instead of calling chat

This is the core decoupling. Replace `send_many_chat_messages` / `send_chat_message` calls with `emit()` calls in all loan services.

**Files:**
- Modify: `app/domains/loan/services/request/create.py`
- Modify: `app/domains/loan/services/request/accept.py`
- Modify: `app/domains/loan/services/request/reject.py`
- Modify: `app/domains/loan/services/request/cancel.py`
- Modify: `app/domains/loan/services/loan/create.py`
- Modify: `app/domains/loan/services/loan/update.py`

- [ ] **Step 1: Refactor request/create.py**

Remove imports:
```python
# Remove these lines:
from app.domains.chat.schemas.base import ChatId
from app.domains.chat.schemas.send import SendChatMessageLoanRequestCreated
from app.domains.chat.services import send_many_chat_messages
```

Add import:
```python
from app.infrastructure.events import emit
from app.domains.loan.events import LoanRequestCreated
```

In `create_many_loan_requests`, replace the chat message block (lines ~185-200):
```python
    # Before:
    if send_messages:
        await send_many_chat_messages(...)

    # After:
    if send_messages:
        for loan_request in inserted_loan_requests:
            item = await db.get(Item, loan_request.item_id)
            await emit(
                db,
                LoanRequestCreated(
                    loan_request_id=loan_request.id,
                    item_id=loan_request.item_id,
                    borrower_id=loan_request.borrower_id,
                    owner_id=item.owner_id,
                ),
            )
```

Also remove the `cache` parameter handling for loan request created — it's now handled by the event handler in `loan/handlers.py`. Remove:
```python
    if cache is not None:
        from app.domains.loan.services.cache import invalidate_loan_request_created
        ...
```

The `cache` parameter can stay in the function signature for now (removing it is a separate cleanup), but the body no longer uses it for this operation.

- [ ] **Step 2: Refactor request/accept.py**

Remove imports:
```python
from app.domains.chat.schemas.base import ChatId
from app.domains.chat.schemas.send import SendChatMessageLoanRequestAccepted
from app.domains.chat.services import send_many_chat_messages
```

Add:
```python
from app.infrastructure.events import emit
from app.domains.loan.events import LoanRequestAccepted
```

In `accept_many_loan_requests`, replace chat message block:
```python
    if send_messages:
        for loan_request in loan_requests:
            await emit(
                db,
                LoanRequestAccepted(
                    loan_request_id=loan_request.id,
                    item_id=loan_request.item.id,
                    borrower_id=loan_request.borrower.id,
                    owner_id=loan_request.item.owner_id,
                ),
            )
```

In `accept_loan_request`, remove the cache invalidation block — now handled by event handler.

- [ ] **Step 3: Refactor request/reject.py**

Same pattern. Remove chat imports, add event imports. Replace:
```python
    if send_messages:
        for loan_request in loan_requests:
            await emit(
                db,
                LoanRequestRejected(
                    loan_request_id=loan_request.id,
                    item_id=loan_request.item.id,
                    borrower_id=loan_request.borrower.id,
                    owner_id=loan_request.item.owner_id,
                ),
            )
```

Remove cache invalidation block from `reject_loan_request`.

- [ ] **Step 4: Refactor request/cancel.py**

Remove chat imports, add event imports. In `cancel_many_loan_requests`:
```python
    if send_messages:
        for loan_request in loan_requests:
            await emit(
                db,
                LoanRequestCancelled(
                    loan_request_id=loan_request.id,
                    item_id=loan_request.item.id,
                    borrower_id=loan_request.borrower.id,
                    owner_id=loan_request.item.owner_id,
                ),
            )
```

In `cancel_item_active_loan_request`, replace the `send_chat_message` call:
```python
    if send_message:
        # Need owner_id — get it from the loan_request_read that's fetched later
        # Emit after get_loan_request so we have all data
```

Note: `cancel_item_active_loan_request` calls `send_chat_message` before fetching `loan_request_read`. Restructure slightly: emit after the `get_loan_request` call so we have `owner_id`:
```python
    loan_request_read = await get_loan_request(db=db, loan_request_id=loan_request.id)

    if send_message:
        await emit(
            db,
            LoanRequestCancelled(
                loan_request_id=loan_request.id,
                item_id=loan_request_read.item.id,
                borrower_id=loan_request_read.borrower.id,
                owner_id=loan_request_read.item.owner_id,
            ),
        )
```

Remove cache invalidation block from `cancel_loan_request` and `cancel_item_active_loan_request`.

- [ ] **Step 5: Refactor loan/create.py (execute_loan_request)**

Remove chat imports, add:
```python
from app.infrastructure.events import emit
from app.domains.loan.events import LoanStarted
```

In `execute_many_loan_requests`, replace chat message block:
```python
    if send_messages:
        for loan_request, loan in zip(loan_requests, loans, strict=True):
            await emit(
                db,
                LoanStarted(
                    loan_id=loan.id,
                    loan_request_id=loan_request.id,
                    item_id=loan_request.item.id,
                    borrower_id=loan_request.borrower.id,
                    owner_id=loan_request.item.owner_id,
                ),
            )
```

Remove cache invalidation from `execute_loan_request`.

- [ ] **Step 6: Refactor loan/update.py (end_loan)**

Remove chat imports, add:
```python
from app.infrastructure.events import emit
from app.domains.loan.events import LoanEnded
```

In `end_many_loans`, replace chat message block:
```python
    if send_messages:
        for loan in loans:
            await emit(
                db,
                LoanEnded(
                    loan_id=loan.id,
                    item_id=loan.item.id,
                    borrower_id=loan.borrower.id,
                    owner_id=loan.item.owner_id,
                ),
            )
```

Remove cache invalidation from `end_loan`.

- [ ] **Step 7: Run loan tests**

```bash
pytest tests/loan/ -v
```

- [ ] **Step 8: Run chat tests (verify messages still appear)**

```bash
pytest tests/chat/ -v
```

- [ ] **Step 9: Run full test suite**

```bash
mise run test
```

- [ ] **Step 10: Commit**

```bash
git add -A
git commit -m "refactor: loan services emit events instead of calling chat directly"
```

---

## Task 8: Refactor item create to emit events instead of calling user stars

**Files:**
- Modify: `app/domains/item/services/create.py`

- [ ] **Step 1: Replace star award with event emission**

Remove imports:
```python
from app.domains.user.services.star import AddUserStars, add_many_stars_to_users
from app.domains.user.star import stars_gain_when_adding_item
```

Add:
```python
from app.infrastructure.events import emit
from app.domains.item.events import ItemCreated
```

Find where `add_many_stars_to_users` is called (in `create_item` or `create_many_items`) and replace with event emission. The star award now happens in `user/handlers.py`.

Also emit `ItemCreated` which triggers both star award AND cache invalidation.

Remove any inline cache invalidation for item creation.

- [ ] **Step 2: Run item tests**

```bash
pytest tests/item/ -v
```

- [ ] **Step 3: Run user star tests**

```bash
pytest tests/user/test_user_stars.py -v
```

- [ ] **Step 4: Run full suite**

```bash
mise run test
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: item create emits ItemCreated event instead of calling user stars"
```

---

## Task 9: Refactor auth validation to emit event

**Files:**
- Modify: `app/domains/auth/services/validation.py`

- [ ] **Step 1: Replace pubsub + cache calls with event emission**

Remove imports:
```python
from app.domains.chat.schemas.pubsub import PubsubMessageUpdatedAccountValidation
from app.infrastructure.pubsub import get_broadcast, notify_user_after_commit
```

Add:
```python
from app.infrastructure.events import emit
from app.domains.auth.events import AccountValidated
```

In `validate_user_account`, replace the `notify_user_after_commit` call and cache invalidation block with:
```python
    await emit(db, AccountValidated(user_id=user.id))
```

The chat handler sends the pubsub notification, the user handler invalidates cache.

- [ ] **Step 2: Run auth tests**

```bash
pytest tests/test_auth.py -v
```

- [ ] **Step 3: Run full suite**

```bash
mise run test
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: auth validation emits AccountValidated event"
```

---

## Task 10: Refactor item like/unlike/save/unsave to emit events

**Files:**
- Modify: `app/domains/item/services/like/create.py`
- Modify: `app/domains/item/services/like/delete.py`
- Modify: `app/domains/item/services/save/create.py`
- Modify: `app/domains/item/services/save/delete.py`

- [ ] **Step 1: Refactor like/create.py**

Replace cache invalidation with event emission:
```python
from app.infrastructure.events import emit
from app.domains.item.events import ItemLiked

async def add_item_to_user_liked_items(db, *, item_id, user_id, cache=None):
    # ... existing insert logic ...
    await db.execute(stmt)

    # Get owner_id for the event
    owner_id = (
        await db.execute(select(Item.owner_id).where(Item.id == item_id))
    ).scalar_one()

    await emit(db, ItemLiked(item_id=item_id, user_id=user_id, item_owner_id=owner_id))
```

Remove the `cache` usage (event handler handles it now). The `cache` parameter can stay for API compatibility but won't be used.

- [ ] **Step 2: Refactor like/delete.py**

Same pattern with `ItemUnliked`.

- [ ] **Step 3: Refactor save/create.py**

Same pattern with `ItemSaved`.

- [ ] **Step 4: Refactor save/delete.py**

Same pattern with `ItemUnsaved`.

- [ ] **Step 5: Run item tests**

```bash
pytest tests/item/ -v
```

- [ ] **Step 6: Run full suite**

```bash
mise run test
```

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "refactor: item like/save operations emit events for cache invalidation"
```

---

## Task 11: Move Region and Category models to their own domains

**Files:**
- Modify: `app/domains/item/models/region.py` — keep only `ItemRegionAssociation`
- Create: `app/domains/region/models.py` — `Region` model
- Modify: `app/domains/item/models/category.py` — keep only `ItemCategoryAssociation`
- Create: `app/domains/category/models.py` — `Category` model
- Modify: `app/domains/__init__.py` — register new model modules

- [ ] **Step 1: Move Region model**

Write `app/domains/region/models.py`:
```python
from sqlalchemy import Identity, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.models import Base


class Region(Base):
    __tablename__ = "region"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f"<{self.__class__.__name__} #{self.id!r} {self.name!r}>"
```

Update `app/domains/item/models/region.py` — remove `Region` class, keep only `ItemRegionAssociation`. Update import of `Region` if needed by the association (it uses string ForeignKey references so no Python import needed).

Update all imports of `Region` throughout the codebase:
- `from app.domains.item.models.region import Region` → `from app.domains.region.models import Region`
- `from app.domains.item.models import Region` → `from app.domains.region.models import Region`

- [ ] **Step 2: Move Category model**

Write `app/domains/category/models.py`:
```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.models import Base


class Category(Base):
    __tablename__ = "category"

    slug: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    parent_slug: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("category.slug", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.slug!r} {self.name!r}>"
```

Update `app/domains/item/models/category.py` — remove `Category` class, keep only `ItemCategoryAssociation`.

Update all imports of `Category` throughout the codebase.

- [ ] **Step 3: Update app/domains/__init__.py to register new model modules**

Add:
```python
from app.domains.region import models as _region_models  # noqa: F401
from app.domains.category import models as _category_models  # noqa: F401
```

- [ ] **Step 4: Verify Alembic sees all models**

```bash
alembic check
```

Expected: "No new upgrade operations detected"

- [ ] **Step 5: Run full test suite**

```bash
mise run test
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "refactor: move Region and Category models to their own domains"
```

---

## Task 12: Update boundary check script and verify zero violations

**Files:**
- Modify: `scripts/check_domain_boundaries.py`

- [ ] **Step 1: Add allowlist for structural dependencies**

Add this constant near the top of the script:

```python
# Intentional structural cross-domain write dependencies.
# These are direct service calls that are allowed (not required to use events).
ALLOWED_CROSS_DOMAIN_WRITES: set[tuple[str, str]] = {
    ("auth", "user"),   # auth creates users, validates credentials
    ("loan", "item"),   # loan checks item availability
}
```

In `check_file`, add a check before flagging violations:
```python
    # Skip allowed structural dependencies
    if (source_domain, target_domain) in ALLOWED_CROSS_DOMAIN_WRITES:
        continue
```

- [ ] **Step 2: Run the boundary check**

```bash
python scripts/check_domain_boundaries.py
```

Expected: "No domain boundary violations found." (exit 0)

If violations remain, fix them.

- [ ] **Step 3: Run full test suite one final time**

```bash
mise run test
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: update boundary check script with allowlist, verify zero violations"
```

---

## Task 13: Final cleanup and verification

- [ ] **Step 1: Run lint**

```bash
mise run lint
```

Fix any issues.

- [ ] **Step 2: Run full test suite**

```bash
mise run test
```

- [ ] **Step 3: Verify boundary check passes**

```bash
python scripts/check_domain_boundaries.py
```

- [ ] **Step 4: Commit any fixes**

```bash
git add -A
git commit -m "refactor: final cleanup after domain boundary fix"
```

---

## Summary

| Task | What | Files |
|------|------|-------|
| 1 | Event bus implementation + tests | `app/infrastructure/events.py`, `tests/infrastructure/test_events.py` |
| 2 | Event dataclasses | `app/domains/{item,loan,auth}/events.py` |
| 3 | Chat handlers (loan→chat decoupling) | `app/domains/chat/handlers.py` |
| 4 | User + item handlers (stars + cache) | `app/domains/{user,item}/handlers.py` |
| 5 | Loan handlers (cache) | `app/domains/loan/handlers.py` |
| 6 | Register handlers at startup | `app/app.py` |
| 7 | Refactor loan services → emit events | 6 files in `app/domains/loan/services/` |
| 8 | Refactor item create → emit events | `app/domains/item/services/create.py` |
| 9 | Refactor auth validation → emit events | `app/domains/auth/services/validation.py` |
| 10 | Refactor item like/save → emit events | 4 files in `app/domains/item/services/` |
| 11 | Move Region/Category models | `app/domains/{region,category}/models.py` |
| 12 | Update boundary check + verify 0 violations | `scripts/check_domain_boundaries.py` |
| 13 | Final lint + test | — |
