from dataclasses import dataclass

import pytest

from babytroc.infrastructure.events import _handlers, emit, on


@dataclass(frozen=True)
class _TestEvent:
    value: int


@dataclass(frozen=True)
class _UnhandledEvent:
    pass


@pytest.fixture(autouse=True)
def _isolate_test_event_handlers():
    """Save and restore the global handler registry around each test.

    Tests in this file register handlers for `_TestEvent` / `_UnhandledEvent`.
    `_handlers` is the application-wide registry populated at import time by
    every `@on(...)` in `babytroc.domains.*.handlers`; clearing it leaks
    across xdist worker boundaries (loadfile dist) and silently disables
    handlers like `award_stars_on_item_created` for any test running on the
    same worker afterwards.
    """
    snapshot = {k: list(v) for k, v in _handlers.items()}
    try:
        yield
    finally:
        _handlers.clear()
        for k, v in snapshot.items():
            _handlers[k] = v


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
