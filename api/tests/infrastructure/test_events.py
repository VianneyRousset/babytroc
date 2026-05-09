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
